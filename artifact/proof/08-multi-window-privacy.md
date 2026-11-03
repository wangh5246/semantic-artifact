<!--
PROVENANCE: copy of outputs/multi-window-privacy-20261101/PROOF.md (v7,
sha256 fb56431479e90869...) registered as G4b 08 for Theorem 5
(Conditional multi-window extension). Review chain: rounds 1-6 with
records in that outputs directory (REVIEW-ROUND1/2/4/5/6.md and external
reports), v7 completion in outputs/multi-window-privacy-v7-completion-20261101/,
and author-authorized third-party re-review completed 2026-11-02.
The deployed contract remains single-release per task and key; this file
extends it conditionally and does not modify files 01-07.
-->
# 多窗口共享状态隐私：条件式联合定理（G4b 接口扩展）— v7

日期：2026-11-01。版本：**v7，THIRD_PARTY_RE_REVIEW_PASS（2026-11-02）**。
v7 修订经作者单席自审（SELF_REVIEW_PASS_IN_DECLARED_MODEL，
outputs/multi-window-privacy-v7-completion-20261101/SELF-REVIEW.md）后，
作者于 2026-11-02 授权并完成第三方重审，状态升级为通过；重审授权记录于
工作区 outputs/（multi-window-privacy-20261101/ 与 re-review-20261102/）。
本文件新增§2(iii)实验实体/观察/后继耦合、§2(v)逐hop复核与预取版macro⑨，
保留旧轮审读文件；v6全文备份与检查见补全工作目录
（outputs/multi-window-privacy-v7-completion-20261101/）。

范围为G4b接口级多窗口扩展，来源模型可选原三key或E′六key模型；
不修改冻结01–07、合同JSON；不声称已有k-释放实现/测试。
本结论只对本文件与依赖中的声明模型负责。
当前稿件已以 Theorem 5（Conditional multi-window extension）引用本文件；
部署合同仍为单释放（每 task/key 一次），该边界在定理陈述中显式保留。

## 0. 结论摘要

现有 G4b 机器是**全执行作用域**的：模拟器各表跨前缀共用（04§2）、状态点按
历史节点只生成一次（04§1，历史本身可跨 window 延续，01§2）、等和条件已按
"每一个允许首曝的完整 R"陈述（04§1）、预算 N/S/V/Q 全为整个有限实验的计数
（07§1）。`E≤1` 是**部署/合同常量**（`max_visible_cohorts_per_task: 1`，
源码 `q_release≤1/task`）；该事实本身不推出扩展。本版§2逐hop与逐事件
补证它在本文MW合同下可以放宽，未扩展到任意输出族。

各版修正（相对前一版）：

1. **v2（轮 1 发现 1/4）**：来源账本 \(\mathcal L\) 参数化——
   \(\mathcal L_{\rm base}\)（07§2 三密钥：330974/80986/5，排除 16385）或
   \(\mathcal L_{\rm ext}\)（论文 Eq. groth-budget / budget-v3.json 六密钥：
   pot14 上 4 把 + pot22 上 2 把 final keys、6 个独立 delta、排除 16385 与
   4194305、degree 规则 k=6）；\(g\) 与 \(B_X\) 由所选 \(\mathcal L\) 一致
   实例化，数值算例（§6）固定 \(\mathcal L_{\rm ext}\)。退化表述去"仅线性"。
2. **v3（轮 2 BLOCKING）**：§2(iii) 条件归纳引理重写为**证明**——显式
   定义 \(\mathsf{Real}_b\) 与 \(\mathsf{Sim}\) 的条件命题，归纳引擎锚定
   04§7 既有前缀归纳（"S 的状态与下一业务输出只依 μ、独立 coins、已收到
   敌手消息、已有理想完整 R 输出及外生 scheduler"），补**真实侧**世界
   无关性论证（隐藏历史进入下一段的全部通道：完美隐藏承诺、(T,m_h)
   精确耦合、CCA 密文、已暴露直方图）；定理不再把引理当前提（§3）。
3. **v3（轮 2 MAJOR）**：退化表述改**乘积项最高三次**——\(e_X\) 含
   \(M_X\cdot B_X\)，\(g_{\rm coll}\) 对 h 二次且 h 随预算增长，故
   \(M_X\cdot g_{\rm coll}\sim t^3\)（全预算×10 情景复算 ×995.86；固定 Q
   情景 ×10.4——**轮 4 勘误：已被 §6 权威值取代（×995.774824 与
   ×10.352303，全 g 口径），且固定 Q 下乘积项亦有正 k³ 项，『最高二次』
   为误，废除**）。v2 的"预算依赖最高二次"为假，已废除。
4. **v3（轮 2 MINOR/NOTE）**：查询/暴露账本分离（发现 5）在 v2 已过审；
   v3 补 §5 的 04§7 行与 E 双定义注（01§3"查询数" vs 07§1"首曝数"）、
   §6 预算约定明示（固定 Q vs 全预算双情景）、§2(iii) C 面护栏（挑战
   条件覆盖全部 k 窗口，弱化即重开预取漏洞面）与空洞性注记、脚本 M_A
   改按 E_enc,A=2k 代入。
5. **v4（轮 3 三项 + 两处衔接 + 两处勘误）**：(a) §2(iii) 按可核验标准
   重写——定义共同抽象状态 Z（全局表/每窗 P/R/L/M/handles/预取值/两账本）、
   真实/模拟状态关系、逐事件类转移核（构包类/Reserve-Bind 类/Send-crash
   类）、共同可达状态上的世界无关性与轨迹级归纳；定理 P/P+A 分支显式
   标注依赖该引理、审读通过前为条件式归约。(b) 退化表述最终修正——
   固定 Q 下乘积项亦含正 k³ 项（系数 ≈6.065×10⁻⁴⁹），删除"约 ×10"
   倍数声称，§6 重定性为提取路由项敏感性分析。(c) M_A 算例双情景
   （E_enc,A=0 标注情景与 2→20 主情景 4,194,328→41,943,100）。(d)
   \(\mathcal L_{\rm ext}\) 显式定义为 E′ 完整来源模型（A1–A4），budget-v3
   仅数值。(e) 新增 §2(iv) A 独立零查询分支（提升 04§5 S_A，不依赖归纳
   引理，不要求等和）。(f) 勘误：A_queried/A_visible 区分；预取不进
   view 改由转移核证明而非先验断言。
6. **v5（轮 4 两席）**：(a) 核 1 改述——真实侧依赖明示（Prepare/native
   transcript 依赖真实隐藏输入，v4"只用该报告自身随机性"混同两侧的表述
   废除），通道清单补 (e) native transcript/proof（Groth16 精确 + 03
   kernel b_N/Tail 计费）与 (f) 时序/长度（01§8/04§7 固定工作同字节
   前提），新鲜随机性独立性引证 04§4。(b) Z 枚举勘误扩全——P/R/L/M/A_L
   括注按 01§3/05§2 改正（P=locked、R=eligible、L=committed、M=applied），
   补 Helper journal/Leader job-lease、quota/证书/outbox、已提交 native
   Σ/z_h，声明 Z 涵盖 04§2 全部 S 表及真实侧对应物。(c) 核 2 补相容性
   推导（01§6 恒等式 + 05§6 公式 + 互斥归属不求和两次）；互斥归属引用
   改"01§3 record 结构 + §1 MW 调度合同"。(d) 轮 3 报告链接修复；§0 v3
   条目加 supersession 标记；A1–A4 摘要补全（A3/A4 原文、6 计数出处）。
7. **v6（轮 5 外部专项+内部两席）**：§2(iii) 按终端 hybrid 结构重写——
   Real_b→J_b 有损链（复用 04§6 hop 计费）+ J_b↔S 的 Rel_b 关系归纳；
   显式定义 Rel_b（五类对象：STATE 单点、固定描述符索引的 Σ/z_h 含
   未提交重算、val_b 估值、payload→V_h,R、可见字节相等）；核 1 通道
   拆 (e1) Groth16（精确 ZK；affine/提取走 B_route）/（e2）native
   transcript（03§4 核，损失 b_N/t_N），末句改引 03§2 per-fixed-x；
   核 3 删独立性断言、改条件非干涉 + 恢复映射（durable/volatile、crash
   二分支、send intent 三分）；核 2 保持义务入 Rel_b（完整门、首 Bind
   符号和、重放不新查询、head 不换早窗、缓存键五元上下文）；A_L 勘误
   为 eligible(L)；Z 补资源计数/HPKE 路由/Register…Freeze 分类；
   "全态同分布"证明目标废除（Z-EXAMPLE-CHECKS 为证明目标反例）。

8. **v7（用户授权补全）**：新增索引实验J_b^(r)、非空setup/prelude初始化、
   Rel_b/Obs与三类后继分布耦合、全事件映射与3×5验证矩阵；逐项复核04§6
   的C_X+10条混合步。macro⑨由F/E/L表示耦合重证允许私有预取时的零观察差，
   不再使用“abort前根本无query”。逐通道合取、腐化向量/seed与世界标签、
   五元缓存键合同导出、资源预算引证及volatile清单同时修正。

**明确的范围限制**：本定理是接口/合同级声明。当前源码实现 `q_release≤1/task`，
不存在 k-释放实现或测试；泄漏剖面包含全部已暴露窗口输出的联合，不声称 DP。

## 1. MW 游戏：k 个预声明释放窗口的联合隐私实验

固定01的参与方、静态腐化集、执行与预算语义；setup/source部分按§3所选模型
实例化，作如下扩展。下文R指带task/profile/selector/window/snapshot的完整
typed cohort上下文（κ见§2(iii)），不是忽略上下文的裸RID集合：

- **窗口调度预声明**：调度 W=(w_1,…,w_k)（每窗口的 task/selector、预定
  slot/资格、交付边界与截止）在 setup 前固定并进入公开骨架 μ；调度非自适应，
  对手不能在执行中新建窗口。同一 task/profile/key namespace；新 namespace
  不在本扩展内。
- **合法历史**：每诚实 owner 的两个完整合法历史 H_0/H_1 跨越全部 k 个窗口，
  每步满足 ADWC 与真实锚点；跨窗口延续从实际已 commit 的 head 继续（01§2
  原文即如此）。状态点按历史节点生成一次，prev/K/别名复制原点（04§1）。
- **理想查询账本与暴露账本分离（发现 5 修订）**：采用 05 的预取语义——
  模拟器在完整 R 的**首次发送准备时**可提前取得一次该 R 的输出并缓存，
  未使用的查询不交给敌手（05"理想证明允许在准备首次发送时提前取得一次
  相同R的输出"）。据此：
  - 每个实际暴露事件蕴含此前已有对该 R 的一次授权查询（查询时刻 ≤ 首次
    发送）；反之**不成立**——预取后崩溃/中止可留下"已查询未暴露"的缓存
    查询。v1 的"未暴露 abort 必无查询"不变量**废除**。
  - 每个不同 R 至多查询一次（缓存复用）；窗口 w_j 恰有一个完整集合
    R_{w_j}，重试复用同一 snapshot，故**不同查询数 \(E_q\le k\)**，与暴露
    结局无关。预算行由 v1 的"E≤k（暴露数）"改为 **\(E_q\le k\)（不同
    查询数）**；暴露账本 X（05）单列，仅用于泄漏记账。
  - 01§6"首次暴露前不得查询"是无预取的更严变体；MW 定理在两种变体下均
    成立（无预取变体中查询=暴露时刻；预取变体只改变查询时刻、不改变不同
    R 查询数上界），以预取变体为准陈述。
- **泄漏剖面（轮 3 勘误修订）**：区分**查询账本 \(A_{\rm queried}\)**
  （全部已发生的理想查询答案，含预取未用值）与其**可见子序列
  \(A_{\rm visible}\)**（已首曝窗口的直方图）。执行前缀的允许泄漏
  \(L_{\le t}=(\mu_{\le t},\,A_{\rm visible,\le t})\)；v2/v3 把"全部理想
  查询答案"括注为"已暴露直方图序列"的混称**废除**。对 A 恒
  \(O_A=\emptyset\)，不变。
- **多窗口暴露等价（挑战条件，仅 P/P+A）**：两合法世界对每个窗口满足
  \(O_C(R^0_{w_j})=O_C(R^1_{w_j})\)（含 sentinel），j=1..k。由 04§1 既有
  条件逐字实例化；强于单释放情形，由环境承担。**A 不适用此条件**：A 分支
  继承 01§5/07§5 的独立结论（无需等和、零查询），见 §2(iv) 与 §3。

## 2. 全执行混合、观察关系与多窗口组合证明

本节在01的有限执行、静态腐化与执行语义内证明接口级扩展；不将04的
单释放结论直接当多释放定理。§2(iii)定义实验和精确关系，§2(v)逐hop
检验扩展。窗口互斥只针对logical report/retained handle，不要求owner或
STATE历史节点互斥。全部资源取全执行公开上限，含失败与未提交重算。

### 2(iii). 实验实体、Rel_b 与三类核的后继耦合

**A. 上下文与状态空间。** 固定世界b、观察者X∈{P,P+A}、挑战历史H_b、
公开μ、静态腐化集及预算B。μ只固定01§2允许的骨架，不包含verdict或
秘密生成时间。每个已锁窗口有唯一完整集合R_w。一个logical report的
window字段不变，retained handle只归属该窗口；共享历史引用使用全局表。

定义全执行机器族 \(J_b^{(r)}\)，r表示§2(v)固定顺序中已经应用的替换数。
\(J_b^{(0)}=\mathsf{Real}_b^{MW}\)；中间级保留该级密码对象的实际编码和
真实业务操作语义，允许内部语义override实现已替换对象；不是把所有
业务判断预先换成“成功”。每个状态为

\[
s_r=(V,D,U,\Gamma_r,I,\mathbf c,\eta,\sigma).
\]

- V：该观察者可见的完整消息/业务表前缀、角色已知输入及head承诺、公开
  版本/资格/状态；不含诚实role私有DB或明文开口。P+A另外含01允许的
  authority业务视图，仍无authority授权私钥。
- D：持久控制状态。逐窗为P_w、R_w、L_w、L_{s,w}、M_{s,w}及
  A_{L,w}=eligible(L_w)，连同完整body/job/protected-step/tag/consumed
  links、install/permit/freeze/abort、reservation与payload。全局为
  Origin/RID/body、head/version/history/anchor、quota、certificate、
  Helper first-input/response journal和tombstone、Leader job/lease、
  outbox/send-intent。完整记录结构和控制操作继承01§3、05§2–§5。
- U：volatile控制与尚未提交计算：Leader重算、事务栈、等待锁、线程栈、
  network buffering；不因在U中出现就算commit/retained/apply。固定报告
  对应的native原始随机变量不随U丢弃而重新抽样。
- Γ_r：04§2全部密码表与该级对象：H/W/E、typed namespace/source日志、
  HPKE完整tuple及唯一授权override、RO全部usage/offset/raw候选/prefetch
  suffix、nonce、STATE节点/别名、native描述符和retained handles。物理
  调用与logical descriptor分计。每个native描述符关联
  \((v_c^{orig},z_c,\text{seeds/blinds/parts},a,b_{jr},r_q,\Sigma,z_h,T,r_c)\)；
  b_{jr}为joint randomness，不是世界bit。03§4 L116的腐化侧向量/seed
  真实生成，z_c=Q_2(腐化原始份额)，z_h=Σ−z_c。root-abort也缓存。
- I：私有理想接口账本与实际暴露身份。**A_queried只存一次**：为
  `κ→(R_w,y_w)`的持久映射，y_w=O_C(R_w)；其domain给查询计数E_q。
  X记录实际可解密发送的κ和时刻；A_visible按X从A_queried投影，
  不再另存第二份答案。无预取的真实早期级可用ghost映射记账，既不改变
  原算法也不把oracle答案交给归约；归约知道H_b并自行计算其值。
- c分协议执行计数c_exec和归约内部计数c_red。c_exec记录被模拟协议的
  T、Q、bytes、签名/解密/封装/流工作与重试，达到01§7的公开协议上限
  按同规则停止，连同停止回复计入观察。c_red另计提取、表维护、oracle
  模拟及提前求和等内部开销：不把S实际运行时间当真实服务墙钟，也不
  把这些内部工作漏出原语参数；07§1的T_red及共同Q/bytes上界须覆盖
  每端点的全部额外工作。05§2/§3只提供stutter/重算的计费对应，不能
  替代预算停止依据。
- η、σ：敌手内部状态及executor/scheduler控制状态。下一动作可等价地
  作为核参数，由同一敌手策略按其真实可见前缀选择；不向敌手开放I。

五元缓存键
\(\kappa=(task,profile,selector,window,snapshot)\)
是**MW合同级细化**，不是宣称冻结实现已有k-selector API。导出如下：
01§3的typed record固定task/profile/window与selector；01§3.7及05§2
要求唯一持久selector/snapshot并关联完整R和实际payload。因此κ唯一
指向该锁定窗口的规范完整记录映射及固定配置/key身份；重试只用同κ。
不同摘要只能经原hash/认证坏事件混同；不能只用未带上下文的裸R缓存。
每窗只有一个κ，故|dom(A_queried)|≤k；重加密次数另计E_enc,A。

**B. 初始化，不以“空历史”代替。** Init_r先执行01§1的setup，使用§3
选定来源模型（扩展时为E′ A1–A4），固定keys/config/manifest、静态腐化
与敌手初态、允许的辅助CRS/source prelude、H_b与μ、B及零使用计数。
允许的prelude已消耗工作加入相应计数/表，不因业务尚未开始而省略。
业务初始化是该协议的enrollment/genesis边界：实际已有的genesis节点、
登记/来源和引用逐个建立，绝非导入任意运行后私有DB。两世界具有相同
公开拓扑；挑战合法性供证明使用，不把H_b坐标交给最终S。

在未替换级，诚实genesis按H_b真实生成；source采样替换级按02/04的
SimSetup/签名服务生成同分布proof，affine/提取/路由异常仍入B_X。
在隐藏点替换后的级，对每个已初始化历史节点一次采样同一均匀子群点，
借Pedersen双射将其与合法H_b开口耦合；后续prev/K别名只引用原点。
腐化owner已知开口的节点不替换。当前head/版本/初始quota由同一初始化
控制记录给定，证书来自同一签名服务，可见编码按本次生成字节计算。
尚无诚实报告的(ii)(iii)域为空；若初始化前缀实际生成报告，则按下述
K1逐个处理并收费，不能直接假定其完成态。I的查询domain及X初始为空，
故(iv)无绑定项；V相等，(v)成立。这样在终端级与S之间得到下面Rel_b
的初始耦合。setup好域失败、source异常和typed碰撞按所属端点计费；
这是有限分布的耦合与bad-event界，不是对任意稀有前缀重新条件化。

**C. Rel_b与投影Z。** 对密码替换已完成的参考状态s和S状态z，Rel_b(s,z)
要求下列五项及相同控制结构/计数同时成立。Z是这些状态的观察充分投影，
不是秘密份额字节相等；估值val_b仅在证明中使用，S无该解密接口。

1. (i) 每个诚实STATE历史节点对应同一均匀点，prev/K/别名图、当前head
   引用、版本/quota控制记录对应。真实开口可不同；腐化已知开口项保留。
2. (ii) 每固定report/body/task/key/nonce描述符对应同一腐化侧
   \(v_c^{orig},z_c,\text{seeds/blinds/parts}\)，同joint/query coins、Σ及
   z_h=Σ−z_c和root-abort状态，真实已收peer输入/响应缓存与S一致。
   Helper exact retry复用journal；Leader未提交重算从同一原始描述符
   重建或复用**同一个**Σ/z_h，绝非每attempt另采样。nonce猜测/编程
   冲突按§2(v)坏事件处理。
3. (iii) 对每个诚实Finish产生的retained handle u_i，具有同一身份、
   session/tag及typed output联系，并有
   \(val_b(u_i)=\mathbf e_{x_i^{(b)}}-v_{c,i}^{orig}\)。non-H的handle保存
   合法解密和真实native执行得到的w_{h,i}；不施加该互补恒等式。apply
   的符号batch和成员映射恰好含各eligible handle一次，warmup不在M。
4. (iv) 完整门及全部retained links成立时，κ的bound payload在参考侧
   是这些handle估值的和，在S侧是
   \[
   V_{h,R}=y_w-\sum_{j\in R\setminus H}\mathbf e_{x_j}
            -\sum_{i\in R\cap H}v_{c,i}^{orig}
            +\sum_{j\in R\setminus H}w_{h,j}.
   \]
   两者数值相等且固定编码相同；已有κ不能换R、明文或links。
   A_queried只在完整合法reservation后的首次发送准备建立；X仅在实际
   可解密发送时追加。崩溃不回退这两个不同账本。
5. (v) Obs_X可见表/回复/消息/已知角色状态与允许公开head逐字相等，
   使用相同敌手动作、同executor coins和已模拟字节生成工作τ、
   Post(τ,敌手调度,外生coins)以及相应计数。不是要求全部程序固定耗时；
   01§8/04§7的秘密处理、定长存储和观察权限前提保持不变。

**D. 观察与后继耦合的精确定义。**
\(Obs_X(s)=(\text{实际授予X的V},head_X,\text{已发送输出/公开状态账本})\)。
head_X是公开承诺/版本/引用，不是隐藏坐标；I中的A_queried及诚实payload
在发送前不属于Obs。A_visible的y_w作为泄漏接口的分析标签，只在X中
相应发送事件后附着；它不凭空变成额外网络消息。敌手策略读取实际
Obs，不读取分析标签/ghost查询。可同时比较增强观察
\(Obs_X^+=(Obs_X,\mu_{\le t},A_{visible,\le t})\)，其相等蕴含实际观察相等。

一次步骤选定a（敌手消息/原语查询、计划内honest source请求、或scheduler
动作）。K_j输出(o,s′,d)，其中o是本次观察增量，d为**协议执行**工作增量；
内部理想查询返回值**不是o**。给定Rel_b(s,z)和相同合法动作a，对终端
参考核及S核定义耦合π_{j,b}(s,z,a)，使其两个边际分别为真实的
K_j(s,a)、\(\widehat K_j(z,a)\)，并满足

\[
\Pr_{\pi_{j,b}}[o_s=o_z,\ d_s=d_z,\ Rel_b(s',z')]=1. \tag{CPL}
\]

这里相等的是c_exec与被模型观察的τ，不是S和参考机真实CPU指令数相等。
c_red允许不同，分别受预定归约资源上界支配；不改变协议预算停止点。
选择预算时须同时给可见协议限额与足够的内部归约上界（07§1），不能
通过在一个端点先耗尽较小内部限额来制造新的观察差异。

这里的精确核是已完成相应替换、使用合法来源路由的参考核；路由/编程
坏事件不被(CPL)隐含删掉。对实际端点使用identical-until-bad：在坏事件
前耦合扩展，首次不满足来源/编程前提的路径交回相应hop的损失界，而非
对“整个执行恰好无坏事件”作归一化条件化。macro⑨两端的路由风险已各
收一份B_X，恢复坏路径不再在公式外加一个未知ε。由此“精确表示坍缩”
指该参考层，实际real/ideal界仍由§2(v)的全部端点费用给出。

这一定义适用于精确替换和终端表示坍缩。**HPKE等相邻有损hop不承诺
精确同观察耦合**：这些级的业务上下文/控制嵌入经同一核递推，唯一
protected对象由原语挑战提供，用全轨迹distinguisher和该hop优势界比较；
其余统计hop用对应坏事件/精确耦合。不能从计算不可区分推导密码字节相同。
因此相邻级J_b^(r)↔J_b^(r+1)的嵌入论证在§2(v)，(CPL)在最终级才应用
于所有事件，二者不是循环引用。

**E. 三类核的构造与保持证明。**

**K1：来源/准备/业务进展。** 内部动作顺序沿01/05，逐个检查typed
context、来源认证、body/RID、实际head/版本/quota与许可。诚实新source
使用下列联合采样；已有source仅恢复固定Γ，不重抽seed/nonce/Σ。
受保护HPKE tuple只走授权H override，其他tuple合法解密并执行non-H
codec/native，未知statement按同一H/W/E路由。腐化role签名不假定诚实。

对诚实报告，03§4给出相同原腐化inputshare/seed和v_c^{orig}，取(a,b_jr,r_q,Σ)
强模拟；r_q为根则两侧同root-abort，否则z_c按实际Q_2计算、z_h=Σ−z_c。
任意peer动作计算同一个Decide(z_h+z'_c)/seed谓词；其错误/Continue/Finish
及未提交重算反馈因此是同一随机变量的函数，保持(ii)。T均匀，r_c按
真实腐化侧开口生成，m_h=T−F(v_c^{orig})−r_c；同一native变量上的receipt
与04§4真实联合分布精确对应，任意m'_c的moment判决亦相同。

**Finish建handle**：成功时reference执行identity-truncate，03§4 L122、
01§6保证输出为e_{x_i^(b)}−v_c^{orig}；S只创建同tag/类型handle并赋上
证明用val_b关系，不打开秘密份额。因此新项满足(iii)，未Finish不建项。
原有handle/早窗payload不动。新STATE节点以满域盲化双射耦合，已有
节点/prev/K只复制，保持(i)。commit核实际检查相同签名/来源/receipt、
moment、head/K/version/quota并做同一CAS，故同结果和相关后继；apply
只把同一eligible handle加入符号和一次。freeze/abort门也从同控制记录算。

观察增量是实际packet/receipt/证书/诊断/peer回复与其允许业务记录。
取相同公共随机币及上述联合分布作为π_1；每个更新字段均按同控制操作
赋值，未更新字段保持。因而(CPL)的输出与后继两半同时成立。其依据是
**逐通道合取**：(a)承诺/别名的完美隐藏，(b)同native变量的receipt联合律，
(c)HPKE归约后的授权路由，(d)许可输出接口，(e1)Groth16精确数学ZK及
已收费affine/提取路由，(e2)03§2 per-fixed-x full-verifier律和03§4
主动核，(f)01§8/04§7执行后处理。per-fixed-x只证明(e2)的数学部分，
不替代其他通道，也不将FLP validity soundness加入隐私界。

**K2：Reserve/Bind。** 先从相同控制状态检查
L_s=P、eligible(L_s)=R、M_s=R及完整retained links。失败时无理想查询，
返回相同错误与控制后继；STATE/Σ/handles/旧payload不变。合法首次
reservation持久化固定κ/完整snapshot后，S在发送准备阶段私下查询一次
y_w，reference从固定H_b与已知/提取non-H声明计算同一y_w。两者都登记
同A_queried键值，payload计算按(iv)。由(iii)逐项求和，诚实部分减去
原腐化份额，non-H加回真实w_h，正好得到reference的真实和；故没有
retroactive改handle或receipt。互斥window保证只求和该窗成员一次。
同时04§4的receipt等式已在K1保持，Bind不重新使用独立moment样本。

已有κ时核检查相同snapshot/links并使用同一既存bytes；不查询第二次。
若合法重算先前尚未commit的payload，也由固定handle表达式给出同一bytes。
STM/CAS和绑定全长比较使用同一值，因此同分支；错误重绑定按公开身份
门拒绝，不把任意攻击者内容送入额外秘密比较oracle。

**本事件观察**是reservation/bind的可见状态、成功/冲突回复、定长存在位
与允许的加密业务记录，不是私有y_w或明文payload。首次查询是内部步骤，
两侧π_2采用同值、同事务结局和执行coins，输出相同。查询/绑定只扩展I
和对应D项；(i)(ii)逐字段不变，(iii)handle恒等式不变，(iv)由求和建立，
(v)由身份门/定长同字节后处理保持。这也证明(CPL)的相关后继，不能仅
从“查询数不增加”推出后继相等。跨窗进展不能改写已冻结的早窗成员。

**K3：发送/重试/故障/停止。** Send只在持久完整κ和bound bytes存在时
取同一payload，按相同加密币封装（无需隐藏的P出站直接真实生成），
在首次可解密交付事件同步更新X；因此Obs^+同时附同y_w标签。exact
retry用缓存bytes；重新封装只增加实际封装/字节工作，不增加查询。
发送后丢ACK保留X；send intent而未实际交付不假称已实际输出，保持05
允许的“可能已暴露”保守状态，不能由未知状态证明零暴露。

crash对同一事务使用相同未提交回滚/已提交二分支。D和私有I缓存保持，
U中线程栈/等待锁/事务外重算/network buffering按同scheduler清除或
继续其已发生发送记录；不能抹去已经离开信任域的消息。恢复后Helper
读同journal，Leader由固定Γ恢复同Σ/z_h、按lease重新争用而不新增source。
全局STATE别名/head及已commit版本/quota保持(i)，(ii)按固定描述符恢复，
(iii)(iv)的持久handle/绑定不动。abort只终结对应许可/阶段，已commit和
已暴露不撤回。预算停止由同计数与01§7规则决定；剩余预算不足时两侧
在同一个primitive/发送边界停，不用秘密值决定停止。

未消费预取值的**条件非干涉**是固定可见前缀、实际动作、控制记录、
允许执行coins后的因果性质，不是与先前输出无条件独立。身份门不读其
内容；合法重绑定比较恒为同一payload；status只EXISTS、固定长BYTEA
禁压缩，工作τ依01§8/04§7由模拟字节/受审固定秘密路径生成。因此除
消费该κ的Send外，缓存内容不形成额外可见分支。先前可见输出与未来
输出相关、敌手据前者选动作均允许。以相同调度/事务coins/加密coins
定义π_3，得到同观察/工作及保持Rel_b的后继，成立(CPL)。

**F. 全事件分类与验证矩阵。** 原程序可把一个事件分解为下表细步骤；
stutter只指业务集合不变，不表示没有回复/CPU/RO成本。

| 操作/子操作（05§5及01§7） | 类别 | 读取与更新；观察 |
| --- | --- | --- |
| Setup/enrollment/genesis/允许auxiliary prelude | Init/K1 | 按B初始化；新节点/source按K1，初始Rel_b逐项验证 |
| Origin/Register/Lock/Install/Permit | K1 | 完整context、P/R、head/许可；实际证书/拒绝/回复 |
| Prepare/Continue/Finish/receipt | K1 | 同Γ/journal/lease/native状态；真实peer反馈/handle/tag |
| authority commit、role commit/Apply | K1 | CAS与eligible符号和一次；证书/回复 |
| Freeze、非发送的阶段控制 | K1 | L=P/无active permit/完整apply；阶段/证书 |
| Reserve/Bind/缓存门重查 | K2 | κ、完整R与links；内部查询、存在位/成功或冲突 |
| Send/re-encrypt/retry/ACK、transport/drop | K3 | 固定payload/X/outbox；实际消息、计数 |
| Abort/timeout/crash/recovery/预算停止 | K3 | 上述恢复映射/计数；真实可见失败/时点 |
| 纯读取/等待锁/事务回滚stutter | 所在操作的K1/K2/K3 | 保留bytes/calls/时序及可见回复；未提交不推进集合 |
| 外部RO/群/哈希/签名/合法非challenge解密查询 | K1的oracle子步 | 相应Γ和c/敌手态；按本级原语接口返回真实答案，不另造业务query |

| 核×Rel_b | (i)点/别名/head | (ii)native/腐化侧 | (iii)handle估值 | (iv)payload/I | (v)Obs及相关后继 |
| --- | --- | --- | --- | --- | --- |
| K1 | 新节点双射耦合、别名复制/CAS | 固定Σ/z_h与真实腐化输入；同peer谓词 | Finish由identity-truncate建立世界b估值；Apply一次 | 无Bind时旧项不变 | π_1逐通道联合分布+同控制更新，CPL |
| K2 | 不改节点/别名/head | 不改固定描述符/Σ/z_h | 只读同一完整links/符号和 | 首次求和/私下查询；重放固定 | 查询不在Obs；π_2含门拒绝/事务结局，CPL |
| K3 | durable复制，未提交回滚不换真实head | Helper缓存/Leader固定Γ恢复 | durable/已commit保留 | sameκ/bytes、X按发送更新；查询缓存不回滚 | π_3同调度/coins，条件非干涉与CPL |

**G. 轨迹归纳。** Init给Rel_b支撑上的初始耦合；按上表和(CPL)，每个
有限前缀的下一观察与相关后继可共同扩展。相同实际可见前缀使同一η
策略选择相同分布的后续动作；σ同理。由01§7有限T/B停止，归纳覆盖
全部前缀与停止轨迹，没有任意稀有前缀上的计算距离断言。
\(J_b^{末}\)仍是“替换后的密码对象+真实业务控制/符号估值”的参考实验；
最后才用以上关系遗忘其H_b、开口/val_b等证明注解，得到可运行的04式S。
末级与S观察精确相同，含未完成/未释放报告、交错窗口与post-exposure失败。

这只是**固定世界的real/ideal证明**。比较b=0/1还必须使用§1对全部允许
窗口（含预取未发送）的等和条件。S在相同μ、共同coins和敌手动作下得到
相同O_C答案，故两个理想轨迹同分布；不能把等和说成可取消的“第二重保障”。

### 2(iv). A的独立零查询分支

A不使用上述O_C接口，也不要求逐窗等和。按04§5，STATE别名共用，
每报告取独立T,U并给(m_0,m_1)=(U,T−U)，与同一native前缀kernel联动；
non-H按合法解密真实执行。诚实输入/sidecar及A可见的aggregate封装经
相应HPKE hop换成同长dummy，export状态只EXISTS、私有payload固定长度。
沿同一D/U事件映射维持该零查询关系，Bind只保留存在/身份/长度的抽象，
不向A模拟器索取未知aggregate。聚合ciphertext先在固定b的归约中以已知
plaintext嵌入，再在终端级由dummy生成；不能先做P+A然后投影。
因此仅增加全执行资源及E_enc,A；本分支的源/执行假设与原模型相同。

### 2(v). 04§6逐hop的MW嵌入与预取版macro⑨

**1. 固定链与归约上下文。** 顺序取sourceproof宏①、C_X个逐cipher
hop、宏②–⑩；这是04§6/07§5的同一组变换，在任何报告首次公开前构造
一致的packet/proof/body/signature，绝不事后改已公开packet。
每一个J_b^(r)由A中的状态、Init_r和B–F的控制调度构成：未替换部分真实
执行，已替换部分调用对应02/03/04构造；真实业务门/失败/时序不被删除。
各r是互斥实验，不把多个端点的内部工作当一个真实执行重复发生。

固定b的归约知道挑战H_b，因而可按需要**在线**计算完整R声明和；non-H
由先验witness/提取提供声明，合法非challenge解密给出真实w_h。单个
HPKE嵌入用所准许的decrypt oracle，原H完整tuple绝不送decrypt；同tuple
只走唯一source override，不同AAD/RID/key/info按04§3正常处理。由此
归约不需要第二个密码挑战、额外诚实子集oracle或未来verdict。最后的S
才删去H_b，使用许可O_C。观察到的早窗输出及敌手自适应消息只是同一
归约上下文的后续工作；预算为全执行上限，不要求这些动作事前固定。

“01无预取变体”和“05预取变体”在机器定义上不同：本文采用05变体。
私有Query只在已经持久Reserve完整κ之后、第一次发送的准备/Bind处允许；
不能在未完整锁定或登记阶段查询。真实早期实验不执行理想RPC；参考
实验用ghost/本地计算语义记录，不对真实服务追加网络可观测动作。
模拟器oracle调用和账本工作纳入归约T/预算，内部多一个query标记不被
当成额外真实服务延迟或把真实墙钟答案交给S。原执行τ继续按01§8生成。

**2. macro⑨先行引理：提前查询、绑定与观察可交换。** 在完整门成立的
持久Reserve κ之后，考虑三个实现同一继续上下文的机器：

- F：真实业务把已固定handle的估值求和、Bind为固定bytes并可能发送；
- E：在相同位置内部查询y_w并按(iv)计算/Bind，在发送前可能失败；
- L：与E使用同一身份/控制/长度状态，但把未知payload保留为κ的符号和，
  到第一次实际Send才求值；同一继续上下文不获知这个内部推迟标记。

由(iii)求和恒等式，**F与E的每一个payload值相同**，不仅最终成功时
相同：nonce/peer反馈只改变哪些记录已Finish，门要求全部固定R完成且
retained links一致。non-H按真实w_h补回，不用C完整性替代P。
Bind合法重算得到相同bytes，全长比较为同值比较；尝试换snapshot/R先由
身份门拒绝。故F/E的事务成功、失败/恢复、字节与工作可按同coins耦合。

E与L在第一次Send前，只对外保持相同的reservation状态、payload存在位、
固定长度、公开成功/错误、被模型授予的业务表/执行工作。L是表示层实验，
不是源码新增lazy计算；其符号和的“bytes存在/相等”操作由05合法可达域
恒等式实现，不能把符号丢失当不存在。查询缓存不控制任何额外分支：
身份/成员门由D决定；状态只EXISTS；合法比较恒为同表达式；定长无压缩
和受审执行语义排除内容工作差异。τ和预算记录仍取同合法路径工作。
因此可通过K1/K2/K3非Send步骤作(CPL)归纳：

  * Reserve后、Bind前失败：E可以已有一项私有答案；F/L未向敌手暴露它，
    同κ重试复用或延迟该值，控制记录不回退。缓存单独持久，不因payload
    事务回滚而允许第二个不同query。
  * Bind后、发送前crash/abort：同binding/存在位与公开状态；未发送的
    y_w不直接或经分支泄露。其后其他窗口仍可继续，同一归纳作用于共享表。
  * 第一次实际Send：L求值得到与E/F相同bytes，更新同X，Obs^+附同答案；
    以后ACK丢失、重试或新封装只操作同一payload。
  * 永不Send：查询差异仅存在于私有ghost/模拟账本；真实观察一直相同。

推迟求值不取消已实际发生的查询：这是E/L的**表示耦合**，E的domain
一直计入E_q。L的符号映射也预留同κ，若比较计数便赋同ghost计数，
不能由“推迟了计算”偷减T或另获集合。以上证明允许未用答案与已暴露
结果相关，既不假设统计独立，也不要求对手不看先前输出。新增窗口时
无需重新开始该耦合：D中其他窗、全局Γ、head和旧payload都按相同动作
演化；logical report互斥使κ求和不改写别窗handle。

于是macro⑨的继续上下文在**所有**前缀（含abort）同观察，非仅最终
SUCCESS。04§7 L146的“之前abort不查询aggregate”在本文被精确替换为：
**未实际发送不向观察者公开该κ答案；已完整Reserve的准备阶段允许一次
私有预取，失败不撤回其查询记录；恢复仍绑定同κ。** 前半的因果性与
每次实际Send的完整R关系是旧hop使用该句的实质用途；旧句中较强的
“根本无内部查询”在F/E/L交换证明中不再需要。因此这不是只改E账本，
而是对macro⑨端点的转移与继续上下文重新给出零差异证明。

**3. 逐hop复核表。** 每行两端另各去掉路由坏事件≤B_X^L，费用统一
收进M_X；表内列的是该hop自身费用。route失败不被当成功路径，未对
任意good-prefix作归一化条件比较。

| hop | k-query/共享表下的归约嵌入 | 预取及04§7因果性用途 | 自身费用 |
| --- | --- | --- | --- |
| ① sourceproof采样 | 每typed source在首次公开前02精确重参数化；同H/W/E跨窗，S含全source/prelude | 固定b归约能算所需完整R，查询时间不改变proof oracle权限；不使用“abort无query” | 数学Z_G16=0；affine/提取入端点B |
| C_X个cipher hop | 按实际新封装次序给一个受保护challenge，其余自行生成；原tuple走唯一override，合法非challenge照常解密 | 准备期私有完整R求值按F/E；给挑战原语的标签/禁解密集合不因查询数改变；早窗输出为同上下文 | Σ单challenge HPKE Adv=H_X |
| ② nonce去重 | 全task诚实N次nonce表，跨窗不清空；同source重算不新抽 | 预取不新增source/nonce；查询可因反馈触发，但预查已含全部Q | N²/W |
| ③ 初始RO编程 | 同一完整usage/seed/binders/offset表；joint/prover/query/parts全执行在线编程 | 输出可适应性影响后续外部RO查询，仍是03允许的有限敌手；只有完整R求值，不能查询hidden verdict | N[Q4+2(Q3+Q6+Q7)+Q5]/W |
| ④ share/part编程 | 腐化向量/seeds真实，隐藏补份额翻译保持(ii)(iii)；同handle一次 | Bind真实和随翻译同步由F/E等式维护；共享STATE不复用report seed | N[Q1+Q2+2Q7]/W |
| ⑤ 移除prover coins | 保留源/RO来源映射，未公开prover seed依03处理，公开seed查原表 | 预取输出不是prover seed oracle；任何猜测/后续查询都在全Q4内 | NQ4/W |
| ⑥ FLP full-verifier | per-fixed合法x和joint/query coins的Σ强模拟，含root-abort；恶意peer多反馈共享同Σ/z_h | 不论该报告最终进入哪窗、是否释放；反馈先于完整R查询也可模拟，不以未来输出补造旧反馈 | Nδ_FL,abort=0 |
| ⑦ hidden points/receipts | 每历史节点一次Pedersen双射；T,m_h与同v_c/r_c精确联动，已知腐化MASK不替换 | 别名跨窗同点、任意m'_c同判决；不用任何aggregate解释receipt，预取不改变它 | 0 |
| ⑧ raw trace耦合 | 对每完整流保存拒绝candidate/accepted/prefetch suffix，已知seed真实展开 | 多窗query/重算只读同流并计实际工作；τ由相同联合字节产生，不输入真实secret time | 0（截断另见⑩） |
| ⑨ 业务/首曝后处理 | 按K1–K3和F/E/L引理，真实控制、H/non-H和、绑定与发送全部对应 | **本小节重证**；不再使用“abort根本无查询”，改私有预取非干涉+同κ发送 | 0 |
| ⑩ strict-PPT截断 | 每source至多五fresh field流，L上限不变；全N并集，实际预取/计算均入T | 私有O_C是有限完整集合求值/理想调用，不产生新拒绝采样流；重试不新流 | t_N=clip(5N·C(10129,129)ρ^129) |

表中C_X是事前上限，未发生的challenge位置填空hop；A的重复aggregate
封装必须计E_enc,A，P/P+A的已知出站payload正常加密，不是隐藏challenge。
所有原语归约的T_red、oracle calls/bytes包含k次完整集合处理和共享表维护；
不能只加E而沿用单窗CPU上限。新集合数量、query时刻不带来新的primitive
challenge类型，故不增加十个macro的数量；实际C_X和资源值可以变大。

**4. 相邻级与终端装配。** 对每个相邻级，固定共同业务上下文和允许
敌手/scheduler，以上行给出唯一被替换对象的原语/统计嵌入。共同上下文
通过K1–K3保持对应控制身份与后继；受保护对象差异由其对应distinguisher
承担，不能在归约中“修复”已经发出的字节。每端点的来源路由/认证/
hash/承诺/setup坏事件由同全执行B_X^L支配。于是

\[
\Delta_X(b)\le\operatorname{clip}\left(
  2(C_X+10)B_X^{\mathcal L}+H_X+b_N+t_N\right).
\]

其中②–⑤费用之和是b_N，⑩是t_N；二者不再乘M_X，不对每个窗口重付
一份。J_b^末↔S的表示坍缩由§2(iii)的Init和(CPL)证明为零观察差。
相同μ、全部窗口等和及同静态腐化使S_0/S_1为同一个理想分布，三角
不等式给Adv_X^MW≤clip(e_X(0)+e_X(1))≤clip(2e_X)。A用§2(iv)独立
零查询关系及同hop表的A封装预算；无需等和。证明完成于声明模型。

这没有证明实现放宽q_release、生产setup、硬件侧信道或DP；自审记录
也不等同外部独立密码学评审。


## 3. 多窗口条件式隐私定理（v7，声明模型内）

**定理（MW）**. 固定 G4b 实例接口与 source 账本
\(\mathcal L\in\{\mathcal L_{\rm base},\mathcal L_{\rm ext}\}\)。
\(\mathcal L_{\rm ext}\) **显式定义为 E′ 完整来源模型**
（[K3-SOURCE-EXTENSION-FINAL.md](../../heatmap_sp2027/artifact/proof/extended-setup/K3-SOURCE-EXTENSION-FINAL.md)
的 A1–A4 假设：A1 两套 phase-1 setup 的独立性；A2 六个独立 delta——
『六』计数出处为 budget-v3.json 的 4+2 final keys；A3 target v5 QAP 不
变、verifier 仅收当前 namespace、无 target 公开 q_i/Delta_r 查询；A4
计数规则为 external→S、inlined→Q），budget-v3.json 仅为其数值预算；\(\mathcal L_{\rm base}\) 为 07§2 三密钥模型。setup 来源部分由
E′ 显式替换，旧 01 的其余参与方/执行语义保留（不重证 E′，准确引用既有
依赖）。释放合同扩为 k 个预声明窗口，同一 task/profile/key namespace，
调度非自适应且进入 μ，静态腐化集不变，全部预算（N,S,V,Q,E_enc,A,
\(E_q\le k\)）为整个有限实验的公开上限。则：

**(a) P 与 P+A 分支**：若两合法多窗口历史满足多窗口暴露等价（§1，仅
此两实验适用），则

\[
\mathrm{Adv}_X^{\rm MW}\le\mathrm{clip}(2e_X^{\rm MW}),\qquad
e_X^{\rm MW}=\mathrm{clip}(M_XB_X^{\mathcal L}+H_X^{\rm MW}+b_N^{\rm MW}+t_N^{\rm MW}),
\]

其中 \(M_X=2(C_X+10)\) 形式不变但**数值随 C_X 随总工作量增长**；
\(C_P^{\rm MW}=C_{P+A}^{\rm MW}=2N\)；\(H_X^{\rm MW}\) 为逐 challenge HPKE
和（challenge 数按 \(C_X^{\rm MW}\)）；\(b_N^{\rm MW},t_N^{\rm MW}\) 以全
执行 N 计（\(b_N\) 含 \(N^2\) 项）。§2(v)给出相邻hybrid嵌入与全部
费用，§2(iii)给出终端表示坍缩与两世界装配；预取和跨窗处理已纳入该证明，
不再将“多窗口归纳引理成立”作为未证明的额外前提。原语、来源及执行
假设仍是定理条件。本版最终自审状态见§8。

**(b) A 分支（独立，零查询）**：X=A 时不要求逐窗等和、不使用任何
\(O_C\) 查询；界同上式但 \(C_A^{\rm MW}=4N+E_{\rm enc,A}\)，由 §2(iv)
对 04§5 \(S_A\) 的逐字提升给出，**不依赖 §2(iii) 引理**。A 的保证相对
01§5/07§5 无范围收窄。

**退化性质（轮 3 修订）**：公式形式不变，各分量按全执行资源重新计算。
**不声称完整 \(e_X\) 的具体增长倍数**——\(e_X\) 还含签名/哈希/HPKE 等
primitive Adv，其时间、字节与查询预算未全部实例化。已计算的提取路由项
见 §6：固定群查询预算、S/V 随 k 线性时，\(M_P(k)\cdot g_{\rm coll}(k)\)
含正 **k³ 项**（\(h_i(k)=a_i k+c_i\)、\(a_i>0\)，复算 k³ 系数
≈6.065×10⁻⁴⁹）；clip 饱和不改变未饱和代数表达式非二次的事实。

**证明。** 先固定b和X。§2(v)对每相邻级J_b^(r)给出原语/统计嵌入，
逐端点路由收费2(C_X+10)B_X^L，自身损失加总H_X+b_N+t_N。macro⑨的
F/E/L证明处理预取后的失败和继续上下文；§2(iii)的Init与(CPL)给出
J_b^末到S的精确观察等价。两合法世界共同μ下，对P/P+A，全部窗口
O_C等和使两个S的query回复及后续分布相同；A以独立零查询S_A装配。
全执行三角不等式即所列界。□

## 4. 重试、崩溃与查询账本（发现 5 修订）

**不变量（替换 v1 表述）**：
1. 每个不同 R 至多一次理想查询：Reserve/Send 持久保留唯一 selector/snapshot
   及实际明文（01§3.7），同 snapshot 重试用同 plaintext（04§4），缓存复用
   （01§6）；重试/重加密产生新 E_enc,A 封装而非新查询。
2. **查询 ⇒ 已到达该 R 的首次发送准备**（预取语义，05）；**查询 ⇏ 暴露**：
   预取后崩溃留下未用缓存值，不进 view、不计泄漏。
3. **暴露 ⇒ 此前已查询**：首次诚实 share 离开受信角色即记入暴露账本 X
   （05），其必经首次发送准备，故查询先行。
4. \(E_q\le k\)：每窗口一个 R、每 R 至多一查；崩溃/中止不改变不同 R 计数。

**反例（违反设计即坏，保留）**：若去掉持久 reservation：崩溃后重发可对
同一 R 产生不同明文或第二次查询（破坏不变量 1），或丢弃已发送 share 的
暴露记账（破坏不变量 3，对手可解密一个从未查询的 R）。二者均使查询账本
失效，正是论文 Table 3 第 5 行（durable execution premise）排除的缺边；
与 k 取值无关。

**回归说明**：k=1 时 \(E_q\le1\)，单释放为特例；无预取变体（01§6）下
查询时刻=暴露时刻，现有 G4b 账本不受影响。

## 5. 与现有来源账本的一致性检查

\(E_q\)/E 在 01–07 与合同的全部出现位置（v3 勘误：补 04§7 行与 E 双
定义注）：

| 位置 | 原文 | v3 处置 |
| --- | --- | --- |
| 01§3 | "task dispatch只允许一个可见selector，故…E≤1" | 调度合同扩为 k；"对每个已允许集合分别保持等和并新增查询账本"即 §1 条件与 \(E_q\le k\) |
| 01§6 | "在授权R首次暴露前不得查询O_C" | 无预取严变体；MW 以 05 预取变体为准，两者均覆盖（§1） |
| 04§1 | "每一个允许首曝的完整R…同一个认证声明histogram" | 逐字适用，实例化为每窗口 |
| 04§6 | C_HPKE≤4N+2E（中间界）；"不能用E≤1抹掉无限重加密" | E_enc,A 计全部 k 次暴露封装，原文即此意 |
| 04§7 | "之前abort不查询aggregate" | 冻结无预取断言；预取变体直接改写其语义（abort 前可已预取）。01§6 双变体论证（§1）兜底：无预取变体下该断言保持，预取变体下以 §4 不变量 1–3 替代 |
| 05§2 | "理想证明允许在准备首次发送时提前取得一次相同R的输出，未使用的查询不交给敌手" | 预取语义的权威出处；查询/暴露账本区分的依据 |
| 07§1 | 预算行 E≤1；E_enc,A 单列 | 预算行改 \(E_q\le k\)（不同查询数）；E_enc,A 不变 |
| 07§5 | C_A=4N+E_enc,A；M_X=2(C_X+10)；宏 hop ⑨ | 公式不变；M_X 数值随工作量增长（§0.2） |
| 合同 JSON | `max_visible_cohorts_per_task: 1` | 常量改 k（未写入冻结文件） |
| 03 头部 | `q_release≤1/task`（实现限制） | 实现层不动；定理为合同级 |
| budget-v3.json / K3-SOURCE-EXTENSION-FINAL.md | 六密钥扩展族（E′ 模型 A1–A4）与 epsilon_setup_sampling | \(\mathcal L_{\rm ext}\) 的权威出处：**E′ 为来源模型与假设、budget-v3 为数值预算**（§3，轮 3 衔接修订） |

**E 的同符号双定义注**：01§3 将 E 定义为"语义输出查询数"、07§1 将 E
定义为"完整cohort语义首曝数"——两处指不同账本对象（查询 vs 暴露），
是轮 1 发现 5 的根源。MW 定理统一用 \(E_q\)（不同查询数）并单列暴露
账本 X，消除歧义。

无其他 E 依赖：b_N、t_N、g、v_N、k_tag 均不含 E。

## 6. 数值算例（精确复算；算例范围不变）

`k_window_recheck.py`（Fraction；固定 \(\mathcal L_{\rm ext}\)）。
**本节为提取路由项的敏感性分析**（轮 3 定性）：未将其他 primitive Adv
置零，也不代表已计算完整 \(e_X\)。

- **g_setup（发现 3 修订）**：权威公式
  \(g_{\rm setup}=1-\frac{p-16385}{p}\cdot\frac{p-4194305}{p}\cdot
  (\frac{p-1}{p})^{10}\)（pot14 X 排除 16385 点、pot22 X 排除 4194305 点、
  10 个须非零变量=2 组 α/β+6 delta），**与 budget-v3.json 存储的精确分数
  相等**（脚本断言通过），值为 1.923726827×10⁻⁷⁰。v1 脚本的重构
  \(1-\frac{p-4194305}{p}(\frac{p-1}{p})^5=1.9162\times10^{-70}\)
  **偏小、非有效上界，已废除**；v1 §6 以"差额很小"辩护的说明同时废除。
- 单窗复算（\(\mathcal L_{\rm ext}\)，论文 Eq. groth-budget 预算）：
  \(g=2.6737\times10^{-50}\)，与稿件算例 2.6738×10⁻⁵⁰ 一致（末位舍入）。
- k=10（S,V ×10、Q/I 固定）：\(g=2.7679\times10^{-50}\)（×1.035239），
  仍 <2⁻¹⁵⁰——仅提取项。
- **完整界（轮 3 修订：不声称增长倍数）**：\(M_P\) 2,097,172→20,971,540；
  \(M_A\) 两情景——无新可见封装（E_enc,A=0，单独标注情景）
  4,194,324→41,943,060，**每角色每窗新封装一次、无额外重加密
  （E_enc,A=2→20）4,194,328→41,943,100**（有重加密须用更大的事前
  预算，不能仅用 2k）；\(b_N\) 3.3685×10⁻²⁵→3.4412×10⁻²⁴（×10.2，
  线性项主导此预算；\(N^2\) 项 ×100）；\(t_N\) 精确为正，
  \(\log_{10}t_N\approx-1992.54\)（高精度复算，float 下溢不当零）。
- **乘积项 \(M_P\cdot g_{\rm coll}\)（发现 4 最终修订）**：
  固定群 Q、放大 source/verify：×10.352303；source/verify 与群 Q 均
  ×10（I 固定）：×995.774824。代数上 \(h_i(k)=a_i k+c_i\)（作者预算
  \(a_i\)=72N₀/5N₀/14N₀，\(N_0=2^{19}\)）、\(g_{\rm coll}\) 为 k 的二次、
  \(M_P(k)=4N_0k+20\) 线性，故乘积含**正 k³ 项**（复算 k³ 系数
  ≈6.065000577×10⁻⁴⁹），固定 Q 亦然；clip 饱和不改变该代数事实。
  v2 的"最高二次"、v3 的"固定 Q 时最高二次"与"约 ×10 退化"均已废除。

## 7. 显式条件与实现/外审边界（v7）

1. **合同级而非实现级**：源码 `q_release≤1/task`；k-释放无实现、无测试。
2. **本轮继续修订与自审**：用户授权完成轮6的hop复合、J_b实体与后继耦合。
   §2已补全这些论证；本文件不把自审当外部独立评审，保留旧轮失败记录。
   当前论文单cohort声明未改。
3. **合同限制**：logical report/retained handle按window互斥，五元κ唯一绑定
   规范完整snapshot；二者是MW合同级细化，已在§2导出/说明，不声称冻结
   实现已有k-selector dispatch。允许重复引用、任意自适应新增cohort未覆盖。
4. **等和条件更强**（仅 P/P+A）：环境须提供 k 个逐窗等和直方图；是前提
   非协议性质。自适应丢弃下逐窗 R 成员随 view 变化，全 j 等和的可满足性
   属环境负担（空洞性风险）。
5. **联合泄漏无 DP**：多个 exact 直方图联合可缩小个体信息。
6. **调度非自适应**；执行中新建窗口不在覆盖内。
7. **同 namespace**；新 task/key namespace 的源模型扩展未做。
8. **A 的 E_enc,A**：无界重加密须由外生预算界定（04§6）；算例的 2k 仅
   对应无重加密情景。
9. **source 账本须固定**：\(\mathcal L_{\rm ext}\) 显式为 E′ 模型
   （A1–A4）+ budget-v3 数值；\(\mathcal L_{\rm base}\) 为参数化备选。
10. **本证明的挑战范围**：§1等和条件覆盖全部k个窗口（含未暴露）。
    若另定义“仅已暴露窗口等和”的游戏，须重新给出自适应可接受性与
    两世界装配；本文未证明该更弱条件，也不据此声称已有区分攻击。
11. **primitive Adv 未实例化**（轮 3）：签名/哈希/HPKE 的时间、字节与
    查询预算未全部指定，故不声称完整 \(e_X\) 的增长率；§6 仅为提取路由
    项敏感性分析。

## 8. 审读记录与本轮自审

| 要件 | 状态 |
| --- | --- |
| 明确联合游戏 | §1（含查询/暴露账本分离、A_queried/A_visible 区分） |
| 逐前缀模拟论证 | §2(iii) Init/Obs/Rel_b/(CPL)/三核/事件矩阵；§2(v)逐hop与macro⑨；§2(iv)零查询A |
| 与现有来源账本一致性检查 | §5（含 E′/budget-v3、04§7 行与 E 双定义注） |
| 重试/崩溃与查询账本 | §4（不变量 1–4 + 反例） |
| 机械小例验证查错 | §6（Fraction 复算，g_setup 权威公式，双预算情景，M_A 双情景，k³ 系数） |
| 独立审读轮 1 | 完成：MAJOR_REVISION，五项发现（[REVIEW-ROUND1.md](REVIEW-ROUND1.md)），未发现满足全部拟议前提的实际协议攻击 |
| 独立审读轮 2（两席） | 完成：MAJOR_REVISION（[REVIEW-ROUND2.md](REVIEW-ROUND2.md)）——C 面预取漏洞显式认证闭合、A/B/D 面无数学反例；BLOCKING 一项（引理为提纲非证明）+ MAJOR 一项（t³ 退化）；席位二：F1/F3/F5 PASS、F4 新增 t³ |
| 独立审读轮 3（单席复核） | 完成：修订后再审（[REVIEW.md](../multi-window-privacy-review-v2-20261101/REVIEW.md)，外部目录）——R3 已解决、R1/R5 主要解决；剩余：核心归纳仍为条件式归约（高）、退化表述（中，k³ 固定 Q 亦然）、M_A 漏 E_enc,A（中）、E′ 衔接与 A 零查询分支两处澄清 |
| 独立审读轮 4（两席） | 完成：席位一 CONDITIONAL_REDUCTION_MAINTAINED（[REVIEW-ROUND4.md](REVIEW-ROUND4.md)）——引理已非提纲、C 面（crash/预取）认证闭合、D 面（A 分支独立）与 E 面（无循环）通过、无数学反例；BLOCKING：核 1 通道穷尽性缺口；MAJOR：Z 枚举错误遗漏。席位二：PASS_WITH_MINOR（轮 3 处置全过、脚本数值全对齐；3 MINOR：链接断链、v3 条目旧值无标记、A1–A4 摘要精度） |
| 独立审读轮 5（外部专项+内部两席） | 完成：外部 [REVIEW.md](../multi-window-privacy-review-v4-z-20261101/REVIEW.md)——§2(iii) 未闭合（缺 Rel_b；核 1 账本混称；核 3 独立性断言无效；A_L 记号错误；核 2 局部代数成立）；内部两席（[REVIEW-ROUND5.md](REVIEW-ROUND5.md)）逐项裁定全部 AGREE/CONFIRM（核 2 代数与 v5 推导逐项一致、check_z_examples.py 亲跑 exit 0；轮 4 行为同一性闭合未被推翻）；Z-EXAMPLE-CHECKS TV=1 为证明目标反例非协议攻击 |
| 独立审读轮 6（两席） | 完成：席位一 MAJOR_REVISION 窄域（[REVIEW-ROUND6.md](REVIEW-ROUND6.md)）——内容无数学错误/反例；(e1)/(e2)/A_L/核 2 义务/核 3 条件非干涉全对；三 MAJOR：J_b 未定义到位、hop 复合静默假设、后继耦合未形式化（含验证矩阵）。席位二 PASS_WITH_MINOR（核 2 义务逐条成立、核 3 无未覆盖路径、一致性 PASS、脚本 exit 0；2 MINOR） |
| v6 历史状态 | 轮6后曾停止；本轮用户明确授权继续，v6原文另存，不覆写历史审读文件 |
| v7 补全与单席自审 | **PASS_IN_DECLARED_MODEL**；四项义务见§2(iii)/(v)，逐项复核见[SELF-REVIEW.md](../multi-window-privacy-v7-completion-20261101/SELF-REVIEW.md)；仅本地自审，不是独立外审/机器核验 |
