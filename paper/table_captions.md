\# Table Titles and Notes



This file is the single source of truth for Table 1–Table 4 in both the Chinese manuscript and the ACM MM manuscript. Numerical values must be verified against the corresponding CSV files before manuscript insertion.



\---



\## Table 1



\### 中文表题



表1 不同回归模型的5折 TimeSeriesSplit 验证性能



\### English title



Table 1 Prediction performance of regression models under five-fold TimeSeriesSplit validation



\### Source



`results/paper\_fig2\_model\_performance.csv`



\### Columns



| 中文列名 | English column | Source field |

|---|---|---|

| 模型 | Model | model |

| MSE | MSE | mse\_mean |

| RMSE | RMSE | rmse\_mean |

| MAE | MAE | mae\_mean |

| R² | R² | r2\_mean |



\### 正式数据



| 模型 | MSE | RMSE | MAE | R² |

|---|---:|---:|---:|---:|

| Best Ridge | 0.1304 | 0.3593 | 0.2639 | 0.8525 |

| Ridge | 0.1306 | 0.3595 | 0.2643 | 0.8523 |

| Best XGBoost | 0.1498 | 0.3858 | 0.2888 | 0.8261 |

| XGBoost | 0.1542 | 0.3915 | 0.2952 | 0.8203 |

| GBDT | 0.1550 | 0.3927 | 0.2964 | 0.8207 |

| LightGBM | 0.1570 | 0.3950 | 0.2990 | 0.8186 |

| Random Forest | 0.1596 | 0.3981 | 0.2997 | 0.8164 |



\### 中文表注



各指标均为5折 TimeSeriesSplit 验证结果的平均值。Best Ridge 在单模型比较中取得最低 MSE、RMSE 和 MAE，以及最高 R²。该表仅用于数值性能比较，不进行统计显著性推断。



\### English note



All metrics are mean values over five TimeSeriesSplit validation folds. Best Ridge achieves the lowest MSE, RMSE, and MAE and the highest R² among the compared single models. No statistical significance inference is made.



\---



\## Table 2



\### 中文表题



表2 不同特征处理方法下 Ridge 模型的预测性能



\### English title



Table 2 Prediction performance of Ridge under different feature-processing strategies



\### Source



`results/paper\_fig3\_feature\_method\_comparison.csv`



\### Columns



| 中文列名 | English column | Source field |

|---|---|---|

| 特征处理方法 | Feature-processing method | model |

| MSE | MSE | mse\_mean |

| RMSE | RMSE | rmse\_mean |

| MAE | MAE | mae\_mean |

| R² | R² | r2\_mean |



\### 正式数据



| 特征处理方法 | MSE | RMSE | MAE | R² |

|---|---:|---:|---:|---:|

| Ridge | 0.1306 | 0.3595 | 0.2643 | 0.8523 |

| KBest20 + Ridge | 0.1389 | 0.3711 | 0.2736 | 0.8424 |

| PCA95 + Ridge | 0.1681 | 0.4085 | 0.3116 | 0.8074 |



\### 中文表注



在当前数据集和验证设置下，直接使用全部38个特征的 Ridge 模型取得最低预测误差。KBest20 和 PCA95 均未带来性能提升。该结论仅适用于当前实验设置。



\### English note



Under the current dataset and validation setting, Ridge using all 38 features achieves the lowest prediction error. KBest20 and PCA95 do not improve performance. This conclusion is limited to the current experimental setting.



\---



\## Table 3



\### 中文表题



表3 Ridge 与 XGBoost 调参前后的预测性能



\### English title



Table 3 Prediction performance before and after tuning Ridge and XGBoost



\### Source



`results/tuning\_comparison.csv`



\### Columns



| 中文列名 | English column | Source field |

|---|---|---|

| 模型 | Model | model |

| MSE | MSE | mse\_mean |

| RMSE | RMSE | rmse\_mean |

| MAE | MAE | mae\_mean |

| R² | R² | r2\_mean |



\### 正式数据



| 模型 | MSE | RMSE | MAE | R² |

|---|---:|---:|---:|---:|

| Ridge | 0.1306 | 0.3595 | 0.2643 | 0.8523 |

| Best Ridge | 0.1304 | 0.3593 | 0.2639 | 0.8525 |

| XGBoost | 0.1542 | 0.3915 | 0.2952 | 0.8203 |

| Best XGBoost | 0.1498 | 0.3858 | 0.2888 | 0.8261 |



\### 中文表注



Ridge 调参后的性能提升较小，Best Ridge 相对基线 Ridge 的 MSE 仅轻微下降。XGBoost 调参后的改善更明显，但整体性能仍未超过 Ridge 系列。



\### English note



Tuning provides only a small improvement for Ridge, with Best Ridge showing a slight reduction in MSE relative to the Ridge baseline. XGBoost benefits more clearly from tuning, but its overall performance remains below that of the Ridge models.



\---



\## Table 4



\### 中文表题



表4 独立融合验证集上的融合模型性能



\### English title



Table 4 Fusion model performance on the independent fusion validation set



\### Source



`results/paper\_fig4\_fusion\_comparison.csv`



\### Columns



| 中文列名 | English column | Source field |

|---|---|---|

| 模型 | Model | model |

| MSE | MSE | mse |

| RMSE | RMSE | rmse |

| MAE | MAE | mae |

| R² | R² | r2 |



\### 正式数据



| 模型 | MSE | RMSE | MAE | R² |

|---|---:|---:|---:|---:|

| Weighted Blend | 0.1766 | 0.4202 | 0.2870 | 0.8190 |

| Best Ridge | 0.1769 | 0.4206 | 0.2882 | 0.8186 |

| Stacking | 0.1790 | 0.4230 | 0.2905 | 0.8166 |

| Best XGBoost | 0.1968 | 0.4436 | 0.3032 | 0.7983 |



\### 中文表注



在相同独立融合验证集上，Weighted Blend 取得最低 MSE，但相对于 Best Ridge 的改善约为0.19%，属于边际数值提升。该表与主模型5折交叉验证结果采用不同评估口径，不能直接进行横向数值比较。



\### English note



On the same independent fusion validation set, Weighted Blend achieves the lowest MSE, but its improvement over Best Ridge is only about 0.19%, representing a marginal numerical gain. This table uses a different evaluation protocol from the five-fold cross-validation results and should not be compared directly with Table 1.



\---



\## Locked numerical facts



\- Table 1: Best Ridge MSE = 0.1304

\- Table 2: full-feature Ridge MSE = 0.1306

\- Table 3: Best Ridge MSE = 0.1304; Best XGBoost MSE = 0.1498

\- Table 4: Weighted Blend MSE = 0.1766; Best Ridge MSE = 0.1769

\- Table 4 must not be merged numerically with Table 1 because the evaluation protocols differ.

