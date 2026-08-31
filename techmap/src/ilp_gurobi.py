import json
import argparse
from gurobipy import Model, GRB, quicksum, Env # Env をインポート
from collections import defaultdict # defaultdict をインポート
import os # os をインポート (ファイルパス操作用)

def load_data_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

#直性PAEに変換する際に使用する関数
def solve_set_cover_problem_gurobi(data, output_filename, threshold=None, time_limit=None, gap_rel=None):
    # 目標の数字の集合を収集
    target_numbers = set()
    for lists in data.values():
        for lst in lists:
            target_numbers.update(lst)

    # モデルの作成
    model = Model("Set_Cover_Problem")

    # Gurobiのログ出力を有効化
    model.Params.OutputFlag = 1

    # ソルバーオプションの設定
    if time_limit is not None:
        model.Params.TimeLimit = time_limit
    if gap_rel is not None:
        model.Params.MIPGap = gap_rel

    # 変数の定義
    x = {}
    for pg in data.keys():
        for idx in range(len(data[pg])):
            x[(pg, idx)] = model.addVar(vtype=GRB.BINARY, name=f"x_{pg}_{idx}")

    # 目的関数の定義 (選ばれるリストの数を最小化)
    model.setObjective(quicksum(x[pg, idx] for pg in data.keys() for idx in range(len(data[pg]))), GRB.MINIMIZE)

    # 制約条件
    for t in target_numbers:
        model.addConstr(quicksum(x[pg, idx] for pg in data.keys() for idx, lst in enumerate(data[pg]) if t in lst) == 1, f"Cover_{t}")

    # モデルを最適化
    model.optimize()

    # 結果を格納する辞書
    selected_lists = {pg: [] for pg in data.keys()}

    # 最適解が見つかった場合
    if model.status == GRB.OPTIMAL:
        optimal_value = int(model.objVal)
        print("最小リスト数:", optimal_value)

        # 上限チェック
        if threshold is None or optimal_value <= threshold:
            print("選ばれたリスト:")
            for pg in data.keys():
                for idx, lst in enumerate(data[pg]):
                    if x[(pg, idx)].x > 0.5:  # バイナリ変数の値を確認
                        print(f" - {pg} のリスト {idx + 1}: {lst}")
                        selected_lists[pg].append(lst)

            # 結果をファイルに書き出し (改行なしで出力)
            with open(output_filename, 'w') as file:
                json.dump(selected_lists, file, separators=(',', ':'))
            print(f"結果は {output_filename} に保存されました。")
        else:
            print(f"最小リスト数が {threshold} を超えています。ファイルに保存されませんでした。")
    else:
        print("解が見つかりませんでした。")

    return model.status


# PAからPAEに変換する際に使用するソルバー関数
def solve_exact_cover_gurobi(pae_instances_found, all_pa_instances, output_filename, time_limit=None, gap_rel=None):
    """
    Exact Cover問題をGurobiで解く。各PAインスタンスがちょうど1つの選択されたリストに含まれるようにする。

    Args:
        pae_instances_found (dict): {pae_type: [[pa_instance_1, ...], ...]} 形式のマッチ結果。
        all_pa_instances (set): カバー対象となる全てのPAインスタンス名のセット。
        output_filename (str): 結果を保存するJSONファイル名。
        time_limit (int, optional): Gurobiの実行時間制限 (秒)。
        gap_rel (float, optional): GurobiのMIPギャップ。

    Returns:
        tuple: (Gurobi Status Code, selected_instances dict)
               selected_instances は {pae_type: [selected_list_1, ...], ...} 形式。
    """
    if not all_pa_instances:
        print("Warning (Exact Cover): No PA instances to cover. Returning empty result.")
        return GRB.LOADED, {pae_type: [] for pae_type in pae_instances_found.keys()}

    if not pae_instances_found or not any(pae_instances_found.values()):
        print("Warning (Exact Cover): No match instances found. Problem might be infeasible.")
        # return GRB.INFEASIBLE, {pae_type: [] for pae_type in pae_instances_found.keys()} # 解なしとして返すことも可能

    print(f"\nSolving Exact Cover Problem for {len(all_pa_instances)} PA instances...")

    model = Model("Exact_Cover_Problem")
    model.Params.OutputFlag = 1 # Gurobiログ表示
    # model.Params.MIPFocus = 1      # 最良目的関数の改善を重視
    # model.Params.VarBranch = 1      # 最良推定（pseudo-cost branching）
    # model.Params.Heuristics = 0.9   # 初期解探索のヒューリスティック強度（デフォルトは0.05）
    # model.Params.Cuts = 2           # 多めにカットを使う（探索空間を削減）
    # model.Params.Presolve = 2       # 強めのプリソルバー

    # ソルバーオプション
    if time_limit is not None:
        model.Params.TimeLimit = time_limit
    if gap_rel is not None:
        model.Params.MIPGap = gap_rel

    # 変数定義: 各マッチインスタンスを選択するかどうかのバイナリ変数
    x = {}
    match_details = {} # (pae_type, idx) -> [pa_instance_1, ...] のマッピング
    for pae_type, instances_list in pae_instances_found.items():
        if not isinstance(instances_list, list): continue
        for idx, pa_list in enumerate(instances_list):
            if not pa_list: continue # 空のリストは無視
            var_name = f"x_{pae_type}_{idx}"
            match_id = (pae_type, idx)
            x[match_id] = model.addVar(vtype=GRB.BINARY, name=var_name)
            match_details[match_id] = pa_list

    if not x:
        print("Warning (Exact Cover): No valid match instances found to create variables. Problem might be infeasible.")
        return GRB.INFEASIBLE, {pae_type: [] for pae_type in pae_instances_found.keys()}

    # 目的関数: 選択するリストの数を最小化
    model.setObjective(quicksum(var for var in x.values()), GRB.MINIMIZE)

    # 制約条件: 各PAインスタンスが「ちょうど1つ」の選択されたリストに含まれる
    covered_pa_count = 0
    for pa_instance in all_pa_instances:
        # このPAインスタンスを含む変数のリスト
        covering_vars = [var for match_id, var in x.items() if pa_instance in match_details[match_id]]

        if covering_vars:
            model.addConstr(quicksum(covering_vars) == 1, f"Cover_{pa_instance}")
            covered_pa_count += 1
        else:
            # このPAをカバーできるマッチが存在しない場合、問題は解けない
            print(f"Error (Exact Cover): PA instance '{pa_instance}' cannot be covered by any match instance. Problem is infeasible.")
            model.dispose() # モデルを破棄
            return GRB.INFEASIBLE, {pae_type: [] for pae_type in pae_instances_found.keys()}

    print(f"Added constraints for {covered_pa_count} PA instances.")

    # 最適化実行
    model.optimize()

    # 結果処理
    selected_instances_result = defaultdict(list)
    status = model.status

    if status == GRB.OPTIMAL or (status == GRB.TIME_LIMIT and model.SolCount > 0):
        print(f"\nExact Cover Solution Found (Status: {status})")
        optimal_value = int(model.objVal) if model.SolCount > 0 else -1
        print(f"Minimum number of selected instances: {optimal_value}")

        for match_id, var in x.items():
            if var.X > 0.5: # 変数が1の場合
                pae_type, idx = match_id
                selected_instances_result[pae_type].append(match_details[match_id])

        # 結果をファイルに書き出し
        try:
            out_dir = os.path.dirname(output_filename)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_filename, 'w') as f:
                json.dump(dict(selected_instances_result), f, indent=4) # defaultdictをdictに変換
            print(f"Exact Cover result saved to {output_filename}")
        except Exception as e:
            print(f"Error writing Exact Cover result to JSON: {e}")

    elif status == GRB.INFEASIBLE:
        print("\nExact Cover Problem is Infeasible. No solution exists where each PA is covered exactly once.")
    elif status == GRB.TIME_LIMIT and model.SolCount == 0:
         print("\nExact Cover Problem: Time limit reached, but no feasible solution found.")
    else:
        print(f"\nExact Cover Optimization failed with status: {status}")

    model.dispose() # モデルを破棄
    return status, dict(selected_instances_result)



########################################################################
#                                                                      #
#                                                                      #
#                            追加した関数        　　　                    #
#                                                                      #
#                                                                      #
########################################################################




if __name__ == "__main__":
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(description='Set Cover問題の解法（Gurobi使用）')
    parser.add_argument('input_filename', help='入力ファイル名 (JSON形式)')
    parser.add_argument('output_filename', help='出力ファイル名 (JSON形式)')
    parser.add_argument('--threshold', type=int, help='上限値（選ばれるリスト数）')
    parser.add_argument('--time_limit', type=int, help='ソルバーの最大実行時間（秒）')
    parser.add_argument('--gap_rel', type=float, help='相対ギャップ（例：0.01は1％）')
    args = parser.parse_args()

    # データをファイルから読み込む
    data = load_data_from_file(args.input_filename)

    # セットカバー問題を解く
    solve_set_cover_problem_gurobi(data, args.output_filename, args.threshold, args.time_limit, args.gap_rel)
