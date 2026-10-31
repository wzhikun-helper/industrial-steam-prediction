# Notebook未确认工作副本：只读差异审查

日期：2026-10-31。对象为notebooks/01_experiment.ipynb；对照整改前提交b9ab96ab9e8938ccb955773cb737c8d51b8dcefc。没有运行、重存、覆盖或暂存Notebook。

## 字节身份

| 版本 | SHA256 | 单元数量 |
|---|---|---:|
| Git已提交版本 | 4f16d2fb73ea396ce5d2d8005425bba57b3104d795986b4cc0be2ac1edeba55a | 171 |
| 本地未确认版本 | 807341c2b04b69c76de2131be29efa424958f49a3a2110759125ee598659b9be | 179 |

前171个单元的JSON内容相同，Notebook顶层metadata相同。差异是末尾追加8个单元（3个Markdown、5个代码单元），不是原有训练单元被替换。Git diff为611行新增；行数含输出序列化内容，不等于611行新算法。

## 单元与风险

下表使用**从0开始的JSON单元索引**，界面按从1计数时加1。

| 索引 | 类型/已保存执行计数 | 作用 | 写入风险 |
|---|---|---|---|
| 171 | Markdown | Fig.5整理小节 | 无 |
| 172 | code / 95 | 已有SHAP聚合结果排序并导出Top-15 | 覆盖results/paper_fig5_shap_importance.csv |
| 173 | Markdown | Fig.3整理小节 | 无 |
| 174 | code / 96 | 特征方法比较按MSE排序、导出 | 覆盖results/paper_fig3_feature_method_comparison.csv |
| 175 | code / 97 | 选取已有Ridge搜索列、按α排序 | 覆盖results/paper_fig3_ridge_alpha_sensitivity.csv |
| 176 | code / 98 | 从三种方法逐折结果计算MSE SD，明确ddof=1，回填并导出 | 再次覆盖Fig.3特征处理CSV |
| 177 | Markdown | Fig.1整理小节 | 无 |
| 178 | code / 99 | 从内存train_data导出target，展示头部、形状与缺失数量 | 覆盖results/paper_fig1_target_distribution.csv |

以上代码没有新模型fit、搜索或SHAP重算调用，但含真实to_csv覆盖行为，仍不能安全Run All。计数95–99只是文件中已保存的历史字段，本轮没有执行这些单元。

## 是否包含唯一研究证据

含尚未进入已提交Notebook的导出过程、样本SD约定和当时执行输出，因此具有独立的**历史来源价值**，必须保留，不能一概视为冗余。Fig.1还依赖当时的内存train_data，单靠追加单元不能完整重建该对象来源。

对应正式CSV已有独立冻结文件和导出/核验入口；这些单元不是新增模型结论，也不能证明未提交内容已经公开。论文导出继续以明确登记CSV为来源，不依赖Notebook内存。

完整diff和逐单元源码/输出类型摘要仅保存在本地隔离运行目录。部分输出含样本头部，不把整份diff或未确认Notebook上传公开仓库。本轮只公开差异分类与字节身份。

结论：**只读审查PASS；发布归属仍待用户确认**。保持未暂存修改，不提交、不运行、不删除。
