# G4b：原生 FLP、隐私模拟与完整查询账本

日期：2026-10-18。固定对象是已验收 G4a 的 `janus-v5-g4a/vendor/prio`，Prio 0.16.8 / VDAF-08，单 task、事前固定 verification key、两个 aggregator、TimeInterval、NoDP、`q_release≤1/task`。本文件不更改 G4a、源、资产或原 run。完整预算的可读接口是 [budget-contract.json](native-budget-contract.json)，原生模拟如何进入全部业务 view 见 [04](04-full-view-simulation.md)。

结论为 **PROVED_IN_DECLARED_MODEL**：下文直接证明本实例 FLP 的含 abort 强 HVZK、两方主动 peer 原生模拟、拒绝采样轨迹及逐项查询界。没有假设“原生隐私已经成立”。RO、正确 setup、底层 primitive 和标准 executor 是明确模型前提；所有数值项来自这些前提中的具体游戏。完整性、诚实失败与隐私损失分列。

## 1. 版本及实际参数

DPRS23 2024-09-25 修订全文 [source omitted from this derivative] 的 SHA 为 `016eb1e83902d30eebc0836b5ca736c40e1bed10841fbc2e4cb5a1f0c447ab98`。使用其中 §2、Theorems 1/2、§C.1/C.2，不用未修订的 robustness 界。它的 p14 写 `s>2`，因此 §4 明确给出 `s=2,t=1` 推导。本文也核对 [VDAF-08](https://www.ietf.org/archive/id/draft-irtf-cfrg-vdaf-08.html) 及 [BBCGGI19 作者保存的 proceedings](https://people.eecs.berkeley.edu/~henrycg/files/academic/papers/proofs-secret-proceedings.pdf)。后者 Theorem 11/Corollary 14 与源码所称 full-version Theorem 4.3 编号不同；源里的“最终输出并非最后 gadget，needs analysis”不被一句文献引用消除，§2自行补齐。本轮 ePrint full PDF 返回403，保留于 读取记录 [source omitted from this derivative]，未宣称下载成功。

真实 `flp/types.rs:320–472`、`flp.rs:229–500,590–746` 给出：

| 量 | 实际值/推导 |
| --- | --- |
| native field | `q=340282366920938462946865773367900766209`，`W=2^128` |
| input/output | `d=10001`；索引0…9999与sentinel10000 |
| gadget | 一个 `ParallelSum(Mul,100)`，arity `a_g=200`，degree2 |
| gadget calls | `ceil(10001/100)=101`，末块仅1个真实输入，其他99对按固定规则补齐 |
| wire 插值节点 | `m=next_power_of_two(1+101)=128` 个单位根 |
| wire / gadget 多项式次数 | 至多127 / 254 |
| proof / verifier | `200+2(128−1)+1=455` / `1+200+1=202` 个field元素 |
| joint / prove / query coins | 2 / 200 / 1 个field元素；one proof |
| shard独立seed | helper measurement、helper proof、两role blind、prove seed，共5个16B seed |
| tag | `08 || 00 || 00000003 || u16BE(usage)`；alg class0、Histogram ID3 |
| 公开key标识 | `vdaf_key_tag=int(SHA256(verify_key)[:12])`，最多96bit；这是metadata，不是上行XOF domain tag |

`new_histogram_multithreaded` 只更换 parallel gadget 执行，数学关系及tag保持相同。`AggregationParam=()`。实际 range-check 没有 draft-08 展示代码中额外乘的一次 `r`；以下按被冻结的 Rust 源推导，不能据草案复制次数。

## 2. 本实例的强 HVZK：含 abort 的距离为零

令合法编码 `x=e_I∈F_q^d`，joint coins为独立均匀 `(a,b)`，query coin为独立均匀 `r`。validity电路是

`R_x(a)=Σ_(j=0)^(d−1) a^(j+1) x_j(x_j−1)`，`S_x=Σ_j x_j−1`，

`V_x(a,b)=b R_x(a)+b² S_x`。

对每个合法x与任意a,b，R=S=V=0。每个chunk的gadget是 `G(z_0,…,z_199)=Σ_(u=0)^99 z_(2u)z_(2u+1)`；输入wire是 `(a^(j+1)x_j, x_j−1)`，末块padding是 `(0,−1)`，之后26个未调用插值位置补0。`ProveShimGadget`在第0节点为每条wire独立采样 `z_l←F_q`，其余节点由这些实际wire值确定。记插值多项式为f_l，诚实proof包括z_l及 `H(X)=G(f_0(X),…,f_199(X))` 的255个系数。

令Ω为128个插值单位根，`λ_0(r)`是第0节点的Lagrange基函数。对 `r∉Ω`，

`λ_0(r)=(r^128−1)/(128(r−1)) ≠ 0`，

`f_l(r)=λ_0(r) z_l+c_l(x,a,r)`。

故对**每个固定**x,a,b,r∉Ω，200个f_l(r)独立均匀；不是只证明平均边际相同。Query的完整verifier为

`Σ=(V_x(a,b), f_0(r),…,f_199(r), H(r))`。

诚实proof使第一项恒0、末项恒 `G(f_0(r),…,f_199(r))`，所以精确模拟器是：先均匀采样a,b,r；若r∉Ω则独立取 `U←F_q^200`，返回 `(a,b,r,(0,U,G(U)))`。该模拟器不知道I；它保留joint coins与完整verifier的相关性。源码的最终validity是101个gadget结果的线性组合加输入的sum-check，**无需等于最后一次gadget输出**；对合法x它恒零，因此上面的分布证明覆盖该源码差异。

实际 `Type::query` 在 `r^128=1` 时返回固定 `FlpError::Query`，并未重抽r。模拟器在同一均匀r命中Ω时也返回同一错误，重复读取同 `(key,nonce)` 时复用它。由此：

`δ_FL,abort = ||View_FL,abort(x)−Sim_FL,abort||_1 = 0`。

这对应DPRS的strong HVZK接口，扩展输出域为固定root-abort；其原文δ用L1总和而非一半TV，本实例为0，因子约定不影响结论。若另以 `r∉Ω` 为条件定义无abort FLP，条件分布仍精确；**不得把该条件游戏冒称真实源均匀r的完美completeness**。诚实source单次原生Query的root失败率为

`p_root=128/q ≈ 3.76158×10^−37`。

此项是失败/可用性概率，不是输入隐私损失。在真实native RO、固定key和均匀新nonce下，联合执行中还可能有RO预查/nonce重复；那些由§5的预算处理，不能再次条件化掉。

### 2.1 分布式 Query 的常数项

源码不是严格齐次的 `Query(x,π)`：每role的电路用 `1/num_shares` 分配常数。记 `Q_s(x_s,π_s;a,b,r)` 为带常数1/s的实际query。插值、proof多项式求值和validity对(x_s,π_s,1/s)都是线性的，故

`Q_2(x_A,π_A)+Q_2(x_R,π_R)=Q_1(x_A+x_R,π_A+π_R)`。

证明逐项相加：seed节点与每个gadget输入wire相加；`x_A−1/2+x_R−1/2=x−1`；padding的两次 `−1/2` 合为 `−1`；sum-check常数也合为−1；query并不本地乘秘密wire，而是从proof系数读取gadget值。因此任意输入/任意proof都满足该关系，不要求Decide成功。r∈Ω时两role都走相同可模拟的root-abort。§4所用 `z_h=Σ−z_c^orig` 用的是这个精确关系。

### 2.2 FLP validity及诚实失败单列

对先承诺的非法x，若S_x≠0，则对任意a，`bR_x(a)+b²S_x`是非零至多二次多项式，漏检≤2/q。若S_x=0而x非法，则至少一个 `x_j(x_j−1)≠0`：否则x全为bit且 `d<q`，sum=1即唯一一热。此时R非零、次数≤d，故

`Pr[V_x(a,b)=0] ≤ d/q+(1−d/q)/q ≤ (d+1)/q=10002/q`。

给定a,b后，恶意prover可选任意455元素proof。Query从它恢复f_l及声称多项式P（degree≤254）。若 `P=G(f)`，第一项就是V_x(a,b)，在其非零时必拒绝；否则 `P−G(f)` 为非零degree≤254多项式。真实r对全F_q均匀且在Ω拒绝，故接受概率无条件≤254/q；若只讨论非root条件实验，界才是 `254/(q−128)`。因此真实含abort接口单次soundness可取

`ε_FLP ≤ (10002+254)/q=10256/q`。

one proof不会把该值平方。原生robustness还须处理恶意客户端离线挑joint seed和key猜测，见§6；P允许腐化role串谋，不继承这种两正确role的输出正确性。

## 3. 七个用途、四种计数与实际字节流

令U_i表示源码usage i。DPRS的RO编号与usage不完全相同，必须明确重命名：`(RO1,…,RO7)=(U3,U1,U2,U4,U5,U6,U7)`。

| usage | seed及binder | 输出、每H source首次需要的接受值 |
| --- | --- | --- |
| U1 measurement | helper xseed；`[agg_id=1]` | 10001 field；Helper init/Finish重展开同流 |
| U2 proof share | helper pseed；`[num_proofs=1,agg_id=1]` | 455 field；Helper init同流 |
| U3 joint rand | jseed；`[num_proofs=1]` | 2 field；每role init复用 |
| U4 prove rand | prover seed；`[num_proofs=1]` | 200 field；client本地生成 |
| U5 query rand | 已固定verify_key；`[num_proofs=1] || nonce16` | 1 field；两role init复用 |
| U6 joint seed | 固定零16B；两个有序joint parts | 16B；Sharding/init/合并prep同表 |
| U7 joint part | role的blind；`agg_id || nonce16 || encode(inputshare)` | 每role16B，共2个；规范10001×16B编码 |

每个TurboSHAKE输入为 `u8(len(dst)) || dst8 || seed16 || binders`，固定场长/完整编码可逆；不同usage不能跨域互换。表中所有RO由**同一张**按完整字节input与offset缓存的扩展输出表实现。task不是所有原生XOF的binder，因此本证明固定单task/key，不悄悄声称跨task独立RO。

必须分别记录：

1. `Q_i`：每usage的全部RO输入/扩展请求，含外部预计算、内部source/role处理及事务回滚重算。重复请求可以保守计多次；distinct descriptor另计，不用accepted field个数代替这个查询数。
2. `A_i`：field接受值个数；H首次完整展开共 `10001+455+2+200+1=10659` 个。U6/U7是seed输出，不是field拒绝采样。
3. `C_i`：实际读取的原始16B候选个数，**包括拒绝候选及32元素buffer的未使用prefetch**。`C_i≥A_i`；重复展开复用原序列，物理工作仍计入运行预算。
4. `B_i`：总RO输出字节；field流为16C_i，seed流16B/次；并记录吸收字节，特别U7的160016B share。primitive/执行层的资源参数用这些字节，不能只看8个用途调用。

`N=N_shard`计全部H诚实构包调用/公开sources，未prepare的公开包也计；`N_prep`计全部进入私密prepare的不同report，包括warmup、eligible-zero、失败和abort前缀，非H也计入实际工作。H handles每报告只有一个；Helper exact journal retry与Leader同原始handle重算都不新增逻辑source/query coins。

然而事务rollback可能重新执行CPU，不能据journal声称只有一次物理调用。令 `C_init,L/C_init,R/C_msg,L/C_msg,R/C_finish,R` 计实际调用次数，含回滚/重试。真实源给出保守而可查的工作界：

`Q_int ≤ 7N_shard + 4C_init,L + 6C_init,R + C_msg,L + C_msg,R + C_finish,R`。

每个stage各自的usage贡献见budget-contract。无重算且两role完整执行时每报告至多20个XOF初始化，只是此特殊执行的工作示例，**不是全局runtime或攻击者cap**。Helper的显式first-input/response journal在private处理前拒绝变化请求；Leader的`leader_continued`位于最终写事务之外，随后由同事务`writer.write + release_aggregation_job`的lease token/expiry fence保证至多一个已提交transition。未提交或失lease的Leader重算可能收到**不同**Helper response，不能泛称所有变化都private前conflict。固定body、report/key/nonce、原始share及已提交状态仍固定同一native随机变量；§4模拟这些额外peer反馈，所有物理calls计入Q/T/bytes。公开外生预算是有界安全游戏的参数，不是源码新增限额，更不是“8 attempts”的总安全界。

## 4. 两方主动peer原生模拟算法

建立一次全task RO/cache/nonce账本，并固定静态腐化角色c、诚实角色h。H仅含被标记的honest-source报告；非H通过04的合法HPKE解密和真实native算法处理。

对每个H，均匀生成nonce n。若c=Leader，采样其显式measurement/proof vectors；若c=Helper，采样其xseed/pseed并从已缓存U1/U2流展开。两种情况下 `v_c^orig` 就是腐化角色原始measurement vector，模拟器知道它，后续不要求c诚实执行。采样blind/parts/jseed并维护U6/U7一致，先固定rands，再在首次公开报告前编程对应RO；冲突事件由§5收费。

从§2精确强sim得到 `(a,b,r,Σ)`。r∈Ω则缓存实际Query错误，不产生新verifier或receipt。否则真实运行 `Q_2` 于腐化原始份额得z_c，并置 `z_h=Σ−z_c`。主动peer给任意z'_c/parts/seed时，模拟器按真实PingPong分支算 `Decide(z_h+z'_c)` 与seed equality，产生真实Continue/Finish/failed；所有谓词只用已知模拟变量。若某角色在该PingPong位置只收到Finish而没有完整verifier，投影同一个联合模拟，不额外泄漏Σ。

这个full-verifier模拟也覆盖Leader未提交重算时收到任意多个不同Helper response：在固定report/body/key/nonce和原始share下，honest init使用相同joint/query coins和同一个z_h。每次 `Decide(z_h+z'_c)`、peer-seed比较及其执行轨迹都是**同一Σ/z_h**的adaptive高效后处理；S逐次计算并遵守真实提交/lease结果，不把它们当新的独立FLP query随机性，也不新增N_shard或δ。源码并未让honest role对未知输入执行一组新query-coins测量。HTTP/rollback重算、可见错误和时序的次数仍全部计物理预算；只有已经提交的唯一transition被导出/引用。Helper已有journal的exact retry仍复用相同字节。若更改实现允许同source换native inputshare、query key、nonce或独立query coins，以上固定Σ论证才失效。

诚实Finish时仅创建保持原始measurement的output handle。实际源重新展开原share再identity-truncate，故对H恒有 `v_h=e_I−v_c^orig`，主动peer改变的是完成/错误，不改变成功output。receipt用04的 `m_h=T−F(v_c^orig)−r_c`，无须打开handle。完整R允许首曝后才按04的H/non-H公式得到诚实aggregate。

DPRS§C.2的s方变换在s=2时逐步仍有定义：唯一honest z；若z=Leader，helper随机vectors减给Leader；若z=Helper，先把Leader显式vectors取均匀，再将隐藏Helper流编程为补份额；`Σ−Σ_T Q`只减唯一腐化query。角色约简wrapper此时为恒等，RO编程、nonce、share翻译与FLP替换不需要第三个role。允许的未提交重算/不同peer response通过上段同Σ后处理直接扩展，不是援引DPRS一次Prep的状态规则来否认该实际路径。新joint/query key、同source新的独立query coins、不同原始inputshare或跨报告重用隐藏seed的扩展不由此覆盖。

## 5. 逐hop隐私损失与hidden seed账本

固定一世界到最终模拟器，设 `Q=Σ_(i=1)^7 Q_i` 是包括内部调用的保守上界，κ=128。采用DPRS§C.2的同一套fresh-input编程，但把uniform field oracle落实为§7的raw stream。以下Q用**源码usage编号**：

| hop | 单世界损失上界；理由 |
| --- | --- |
| nonce去重 | `N²/W`；覆盖诚实nonce生日重复，不将malicious选的RID当随机 |
| joint/prover/query/seed初始编程 | `N[Q4+2(Q3+Q6+Q7)+Q5]/W`；program已有entry，分别须猜prover seed、jseed/part/blind或尚未公布nonce |
| measurement/proof/part改为随机share分布 | `N[Q1+Q2+2Q7]/W`；s=2的helper种子/两blind编程冲突 |
| 移除未知prover coins再用full verifier | `N Q4/W`；猜中从未揭露的prover seed才看到无法同时保持的原proof coins |
| full-verifier强sim | `N δ_FL,abort=0`；§2的条件分布，不是nativeprivacy假设 |
| wire/receipt/time后处理 | 0；04证明联合等式与缓存，不给额外secret oracle |

因此可审的一世界界为

`b_N = N δ_FL,abort + [N² + N(2Q4+2Q3+2Q6+4Q7+Q5+Q1+Q2)]/W`，

其中δ=0。用Q总代替各项可得 `b_N≤[N²+4NQ]/W`；若沿DPRS印出的较宽界，则两世界可取

`ε_N,priv ≤ 2N[δ+(Q+N)/W+2Q/2^127]=2Nδ+(10NQ+2N²)/W`。

本文组合用较直接的 `2b_N`；b_N内部的各native子loss相加后不再乘外层route系数。04/07为每一相邻实验两端各计一个完整执行的SHA/auth/origin/G16等route坏事件，不能在没有master coupling时自动跨所有hybrid只收费一次。统一分解为C个HPKE-hop加10个宏hop：source-proof采样、nonce去重、initial RO编程、shares/parts编程、prover coins移除、FLP full-verifier、hidden point/receipt联合、raw trace耦合、业务/首曝后处理、strict-PPT截断。因此route系数取 `M_X=2(C_X+10)`，完整公式见04；native每个有损子hop也包含在这些端点内，不漏其两端失败概率。

上界最后与1取min。各native hop只计fresh编程冲突；公开或敌手已知seed之后的合法查询读取已编程表，不按每次请求重新抽样。seed碰撞也不能被忽略：后一个调用重用前一个内部entry就是冲突，因Q已含内部调用而被上述 `NQ_i/W` 覆盖。若单列一批n个同域均匀seed，生日项 `n(n−1)/(2W)` 可作为更细分配，但不能再作为独立事件重复收费。

共享固定key允许敌手事先知道/选择key；fresh nonce使其不能事后安排该诚实报告的query r。预先U5(key,n)查询由 `NQ5/W` 付费；事后key替换不在游戏内。提前抢占诚实RID的origin猜测另由04的origin接口和07统一nonce表处理，不能把该通信/认证事件藏入native δ。

## 6. 完整性中的离线grinding及birthday项

在C中两role正确，verification key在诚实setup中正确均匀采样，**客户端未获key，但见其公开96bit tag**，且key在nonce/source前固定；Q包含所有离线候选及内部查询。P/P+A中的腐化role可以知道或事前选择key，那是隐私游戏的能力，不能搬入本robustness定理。若C对手获完整key，则可对其自选nonce精算query r并编造仅在r满足的P(r)，本段不适用。令P为不同的合法首次prepare攻击尝试数，含失败，按受保护完整input而非最终R计数。将§2.2的数值代入修订DPRS§C.1，并将**实际公开tag的条件泄漏**计入两个secret-key hop，在同一可逆域编码与RO模型下，s=2两hint的提取/seed比较步骤照常成立，得

`ε_N,valid ≤ min(1, (Q+P)·10256/q + 2κ_tag + (2P+Q)²/2^128)`，

其中不增加primitive前提时可取`κ_tag=min(1,Q/2^32)`；使用下面明确的SHA随机输入单向性primitive时可取二者的min。Q仍是整个实验的保守调用上界。

**公开tag的平均猜测lemma。** 设均匀K有W个值，公开Z=f(K)取值数至多`2^96`，不假设f是随机函数或各纤维等大。固定其余独立coins，对每个z，攻击者在尚未命中K的lazy-U5游戏中至多查询Q5个候选key，形成集合A_z；此前非命中oracle回答与K条件独立。于是

`Pr[K∈A_Z] = (1/W) Σ_z |f^−1(z)∩A_z| ≤ min(1, 2^96 G5_ext/W)`。

`G5_ext≤Q5≤Q`只计**攻击者外部**U5查询中实际出现的16B候选key，包括offline和重复候选。自适应候选可在不命中分支展开成同一至多G5_ext的序列，取coins期望后同界。真实honest role的内部U5用隐藏key-handle，不是猜测，也不交给下述候选扫描器。Q5作为外部+内部调用总数可保守上界G5_ext，故两个替换hop合计至多`2·2^96 Q5/W≤Q/2^31`。这里只用均匀key与tag长度，不借SHA-CR推出preimage安全，更未默许给定tag仍有128bit均匀熵。源码 `g4a_native_stack.py:182`、`g4a_native_drivers.py:745` 给出实际12B tag；本轮独立 key-tag检查 [source omitted from this derivative] 及输出记录其hash/位置。公开tag在P本来就允许获key的隐私游戏中不改变§5的nonce猜测界。

**标准单向性corollary及完整归约。** 定义`Adv_OW128^SHA256(T_ow,Q_ow,B_ow)`为：挑战者取`K←{0,1}^128`，给归约完整`h=SHA256(K)`；归约输出任意k'使`SHA256(k')=h`的成功率（输出其它preimage也赢）。这是随机128bit输入分布上的普通hash单向性游戏，不是wrapper/native安全假设，不由collision resistance推出，也不把SHA改成随机预言机。

给定该挑战，归约给C对手的key相关配置仅为`int(h[:12])`；其它task/HPKE/认证参数正常独立生成，所有用tag签名/hash的业务字段从同一tag构造。它不知K，故honest U5调用按`(hidden-task-key-handle,nonce)`在**同一**lazy native-RO表中保存输出及03§7的完整candidate流，重复nonce读取同表。其余native用途、source、正确roles、authority、网络/数据库与C全部业务反馈按真实算法执行。每当对手发出一个外部U5查询，解析其16B候选k，先计算真实`SHA256(k)`：若等h，立即输出k赢OW；否则才返回对应外部RO表值。honest内部hidden-handle调用绝不送入该检查。

在首次候选hash匹配前，该归约与相应secret-U5替换游戏精确耦合：若外部候选真为K就必匹配而停止；未停止时所有外部key均不等K，故内部hidden-handle与外部descriptor不别名，其RO/candidate流均具有真实独立分布。提前命中其它preimage只增加OW成功率。其余观测仅从tag及这些已模拟U5输出生成，因此不存在还需要K才能计算的公开字段。于是任一hop的first-key-hit概率≤该归约的OW成功率；扫描全部候选无需猜中位置，**没有G5_ext或Q5倍的advantage损失**。可取

`κ_tag=min(1, 2^96 G5_ext/W, Adv_OW128^SHA256(T_ow,Q_sha+G5_ext,B_sha+16G5_ext))`。

这里Q_sha/B_sha含对手离线工作及整个wrapper全部SHA；额外每外部候选一次16B hash检查，T_ow含这些检查、完整wrapper/role模拟与RO日志维护，不只取攻击者时间。统一有限预算可用Q5代G5_ext。每个secret-key替换hop单独构建该归约，故总界仍为2κ_tag，不声称共享同一个成功事件跨hop去重。

该接口的源码条件可以直接审计：两个provision函数仅给正确role的私有`internal/test/add_task`配置传完整key，返回给业务控制方的是96bit tag；task-id、tokens和HPKE keys独立生成。Prio的生产路径`derive_query_rands:534–542`只把verify_key用于U5；`prepare_init:1303`调用它，后续反馈由该query流派生。C不获得正确roles私有配置或管理员传输，符合01；该key相关通道不是本corollary增加的白名单。若部署另外公开完整key、另一独立key摘要或key相关私有日志，此归约不适用，须重算公开函数范围或另给模拟。

这里的游戏链不是把一个未知native validity符号作为前提：

1. 新的受保护nonce/context只产生一个已提交prepare分支；Helper exact retry复用结果，Leader未提交重算沿固定原始state/coins。完整C成功需要两role的receipt/Finish，故两者在Finish检查的joint seed必须同为由最终有序part向量得到的seed；不一致的运行不能成为完整导出中的counterexample。可以使用DPRS的更强中间游戏处理失败运行；其secret-key替换损失按实际tag归约至多κ_tag。
2. 用正确均匀、仅有96bit公开tag的verify key把U5(key,nonce)改为每个新nonce的独立均匀query r，区分需命中真实key，损失≤κ_tag。失败输入和外部offline U5查询仍计G5_ext/Q5；不是只计最后P次成功。
3. U6的输入是两个有序part，U7输入含role、nonce及完整inputshare。禁止重复joint seed的辅助游戏中，distinct U6 query或匹配其part向量的两组U7输出碰撞（包括offline先查询再提交）总量由全部 `2P+Q6+Q7` 个相关记录界定。若外部先给尚无U7原像记录的part值并先查U6/U3，之后真实U7必须命中该预设part目标才能实现它；这种延迟原像命中同样按目标数×新输出数/W计入该平方上界。对128bit seed给保守并集/生日界 `≤(2P+Q6+Q7)²/W`。重复同一个descriptor读缓存不算新的随机输出；不同nonce要复用已有part tuple，须同时命中对应域中的U7输出，s=2时这个概率至多同一保守界。这里是修订版补入offline Q的步骤，不能删回P²。
4. 对每个fresh U3(jseed)建立在线反查：由已记录U6的part向量和U7完整输入得到已承诺的native总input x。不能在看过joint coins后换x；这样的替换要求上一步的seed/part关联失败。若U3先发生于真实role内部而非外部，就在同一记录建立反查。lazy RO在该次U3提供独立均匀(a,b)，恶意prover之后仍可自适应选proof，恰是§2.2单次FLP soundness实验。
5. 猜测一次可能成为首次获胜的fresh U3位置，在至多 `Q3+P` 个offline/online候选中嵌入FLP挑战；其conditional接受概率≤10256/q，故该项 `≤(Q3+P)10256/q`。两份query的常数相加关系已由§2.1证实，s=2不需要第三个aggregator；具体wire输入/tuple可逆，提取的x是实际share之和。将Q3/Q5/Q6/Q7分别用Q保守替代即得上式。

第一项是对joint randomness的离线grinding与在线尝试；第二项为给定公开tag的verification key/RO猜测；最后一项包括离线joint seed birthday碰撞。info-only fallback使Q约2^20的例子仅有约2^−11的C上界，Q≥2^31时该fallback已平凡；带OW corollary则保留显式primitive advantage，不能将其擅设0来宣称128bit整体完整性。不得换回已撤回的仅P²项，也不把Q取成客户端HTTP的8次局部重试。Query根失败只能减少恶意proof接受率，不必给上式新增128/q；诚实N_prep个输入的root失败union bound另为 `min(1,128N_prep/q)`，必要时再加native预查/碰撞事件，不能说这些诚实输入必成功。

P/P+A的一role恶意情形不提供该完整性结论。腐化owner与role可让non-H实际native输入不同于其声明，04直接解密真实计算其诚实output；native validity误差不作为P隐私的未实例化“ε_native”。

## 7. 接受值与拒绝轨迹：精确联合编程

真实Prng一次prefill32个16B候选，接受little-endian整数 `<q` 并做Montgomery转换；其field值与接受整数为双射。设 `ρ=(W−q)/W=516508834063867445247/2^128`。fresh均匀流中，第i个接受值为Y_i，之前拒绝数K_i，则对任意k_i≥0,y_i∈F_q：

`Pr[K_i=k_i,Y_i=y_i]=ρ^k_i/W = (ρ^k_i·q/W)·(1/q)`。

多值向量乘积仍成立：全部K与全部Y独立。故先按native/FLP混合确定同分布的接受值Y，再为每个Y插入独立Geom(q/W)的K个均匀 `q,W)` 候选，最后拼接little-endian bytes，即得到正确raw RO流；32元素prefetch的尚未消费suffix补独立均匀块。不存在 `N_candidate·ρ` 近似损失。

必须按 `(dst,seed,binders,raw-offset)` 保存完整候选序列/已接受位置/未消费prefetch。Helper Finish、rollback重算、exact retry、后来对同RO输入的查询读取同一流，不重新插入几何拒绝；对手已知或自选seed则从真实同表直接展开。接受值编程与已存在的raw prefix不兼容属于§5的已有entry冲突，不能只缓存接受field而忽略原RO字节。

若归约要求strict PPT，给**证明里的模拟器**一个事前公开fresh stream搜索前缀预算 `C_acc≥L`（不是修改真实runtime）。L个接受值未在C_acc个候选内完成的精确尾概率为

`Tail(L,C_acc)=Σ_(j=0)^(L−1) binom(C_acc,j)(q/W)^j ρ^(C_acc−j)`。

对每个fresh隐藏stream分别求和；重复流只用同一随机K，不产生独立尾事件。取 `C_acc=L+128`，实际32候选buffer预取需另给 `C_raw=32 ceil(C_acc/32)` 的原始候选生成预算，bytes与T都按C_raw而非C_acc计算。这个额外至多31的suffix不扩大尾概率：模拟器在搜索第C_acc项之后即停止，所需raw buffer至多C_raw，费用仍可保守用 `binom(C_acc,129)ρ^129`。至多5N个fresh H field streams、最大L为10001，故总尾可取 `5N binom(10129,129)ρ^129`。恶意自选流的扩展工作由外生Q_raw/时间预算计，不假装具有fresh seed尾分布。若使用期望PPT归约，则几何期望 `L·W/q`，不需额外tail项；本轮contract选择strict版本，04/07不可一边用严格时间T一边隐去尾界。

## 8. 检查与范围

[check_native_privacy.py [source omitted from this derivative] 是独立小field的Prove/Query、Lagrange与raw stream枚举，没有调用native/prover/TLC。初轮 check-r1 [source omitted from this derivative] 核235,824个exact Prove/Query组合（含a/b为0、root abort及完整verifier），2,176个带常数的分布式Query组合、4,225条拒绝采样raw路径、6,561个任意non-H输出的聚合恒等式，并保留错误重抽count/全R短式的反例。扩展 check-r3 [source omitted from this derivative] 另核84,375个partial final chunk及未调用插值节点zero-padding的exact分布组合，合计333,161项，16个只读source pins匹配且实际观察到exit0。r2相同结果及其中断wrapper记录保留，未伪称观察到r2退出状态；本次仅精化文档，不重复执行未变化脚本。它们核对有限代数/实现接口，不机械证明RO/primitive假设。

新增 check_public_key_tag.py [source omitted from this derivative] 的 独立结果 [source omitted from this derivative] 穷举65,792个确定性tag函数、131,840个平均猜测界及14,040个first-hit/list-inversion蕴含，保留忽略tag会失效的反例，并固定两个provision源及Prio源码。原333,161项结果没有combined C界或其数值例值；其FLP单次界仍有效。旧合同的untagged C公式/例值由 keytag-supersession [source omitted from this derivative] 明确撤回，保留原始字节，不作为本版本C验收。

最终source与G4a冻结文档只读复核见 delivery-check-r4 [source omitted from this derivative]，Helper/Leader精化对应05的check004源码锚点。所有abort前缀、warmup、未prepare公开source、事务重算、外部offline查询纳入预算。整个结论没有增加physical location、DP、恶意authority、双role腐化、adaptive corruption、自由key rotation或任意物理side-channel保证。
