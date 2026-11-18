# 原始资料契约

所有机构、车辆、单据和设备均为本地合成，不来自新闻中的真实企业，也不声称新闻发生过这些事件。

原始CSV列为row_id,revision,vehicle,trip,side,weight,at,ref。device/boot从文件清单取得，行身份是device/boot/row_id/revision。weight精确到0.001 kg；at含时区。side为gross或tare；一条gross通过ref引用同代际的tare行row_id。有效配对仅有一个现行gross及其唯一有效tare，毛重不得小于皮重。trip只在device/boot中有效；vehicle不是配对主键。unknown side、格式坏行或小数溢出须保留原行及位置。
原始行版本替代以revisions中的cancels_revision明确指定，没有声明不能按最大修订号猜现行。同身份不同字节是冲突，不拿一份覆盖。被撤销行原件继续保留。归并后的输出按业务日与设备组织，但物理布局不限制。
python -m materials.generate --out /tmp/weighing --rows 1000000 生成规模输入，约90%行属于V-heavy，引用跨文件且有整段重传。rows是合法基础行目标数，另有重传及坏格式；生成器按小批写文件，不计算净重或任何入仓结果。测试资源口径为含所有子进程的总RSS 384 MiB，临时磁盘最多2 GiB；大输入不要求常驻内存，生成器不计入产品资源测量。
随资料提供的小样本故意含同身份异内容、负净重及没有被引用的皮重，输入检查能读取它们不表示它们业务合格。

seed.json与同名Parquet保存相同的输入值，actions.json中的后续动作尚未处理。inventory.json只校验原件物理完整性，不是仓库目录或业务结论。所有后续仓表与接口均待开发，源码不规定其架构。
