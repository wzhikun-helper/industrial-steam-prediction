\# Source Code Directory



本目录用于保存工业蒸汽量预测项目中可复用的 Python 源代码。



\## 当前状态



目前项目的主要实验流程集中在：



`notebooks/01\_experiment.ipynb`



因此 `src/` 目录暂时没有拆分出大量独立 Python 模块。



后续如果需要进一步提高项目工程化程度，可以将 Notebook 中重复使用或具有独立功能的代码逐步迁移到本目录。



\## 建议的后续模块



后续可以按照功能拆分为：



\- `data\_utils.py`

&#x20; - 数据读取、数据检查和基础预处理函数。



\- `features.py`

&#x20; - 特征筛选、标准化、PCA 等特征处理方法。



\- `models.py`

&#x20; - Ridge、Random Forest、GBDT、XGBoost、LightGBM 等模型构建函数。



\- `evaluation.py`

&#x20; - MSE、RMSE、MAE、R² 计算和交叉验证结果整理。



\- `fusion.py`

&#x20; - 加权融合和 Stacking 相关代码。



\- `explain.py`

&#x20; - SHAP 特征重要性和可解释性分析代码。



\- `visualization.py`

&#x20; - 模型比较、残差分析和科研绘图相关函数。



\## 设计原则



\- Notebook 主要负责展示实验流程和结果；

\- `src/` 主要负责保存可复用代码；

\- 避免在多个 Notebook 中重复复制相同代码；

\- 重要函数应具有清晰的输入、输出和必要注释；

\- 后续 Skill 和论文复现实验可以优先调用 `src/` 中的公共函数。

