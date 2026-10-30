# G4b：Groth16 完整提取定理与显式查询账本

日期：2026-10-18。状态：**PROVED_IN_DECLARED_GENERIC_MODEL；EXPLICIT_BUDGET_CONTRACT**。本文件重新证明冻结 G4a W4 的数学链，并补足实际公开 setup 家族、查询和 degree；不把 G4a 的 PASS 当证明。没有改动 G4a 文件、runtime、电路、key、manifest 或旧 run。

结论仅针对 typed opaque generic asymmetric bilinear groups、所列独立 source/RO 模型、正确 setup、静态腐化及精确 origin/body 路由。它不是原 BKSV 的 AGM 定理、strong-SE、黑盒提取、UC、任意真实曲线算法或生产 ceremony 认证。机器可读接口为 [budget-contract.json](groth16-budget-contract.json)，独立只读/精确有理数检查为 audit_budget.py [source omitted from this derivative]。

## 1. 冻结基线、文献与本次新增发现

输入 authority 是最终计划 §9 和 theory-obligations；冻结 G4a 02 [source omitted from this derivative] SHA 为 `5388fbd9d2ce8cbbb73d50096f0cb6e57edece105e01d8c1be0a0fb521c9f864`。新 g4a-assets-001 manifest SHA 为 `dea0403774b5540404b148604a96826f11ce6b44bb18bc2993654d6bc1f94b6c`。

一手全文沿用已保存、已逐页核验的作者版本：[Groth/UCL](https://discovery.ucl.ac.uk/1501201/1/Groth_SNARK9.pdf)，Theorem 3 与§2.2；[BKSV/Edinburgh](https://www.pure.ed.ac.uk/ws/portalfiles/portal/251634012/Another_Look_BAGHERY_DOA03122020_AFV.pdf)，Definition 1、Fig.1、Theorem 1–3 及完整证明。原件 SHA 与页码在冻结 retrieval.json [source omitted from this derivative]。Groth 的原始提取是 generic bilinear-group 结论；BKSV 的 weak-SE 只对未查询 statement 提取，原构造独立随机 gamma。本文重新给 gamma=1 的证明，未把其假设直接删掉后套用原文。

**新增的实际来源义务。** 本次完整枚举发现 `runs/g1-circuit-001/hadwc_genesis_state.DEVELOPMENT.zkey` 是另一份完整公开 key，SHA `4a481ed6c72e0390fd31ca5b00dc04291a87b3e3379122b57a62979a74335b9e`。它与当前资产共享同一 phase1，却有独立的历史 phase2 delta。故实际 source 家族有三个 delta，不能只按新 manifest 两个 key 计 degree。G4a 的一般 k 关系论证仍适用；本次具体账本将 k 设为 3。

另独立补全一个原证明未用的对称提取分支，说明 G4a 的“G2 中 alpha 系数 h 没有 unit”是充分而非必要条件。该加强见§5.4；不追写冻结 G4a。

## 2. 实验、模型与全部辅助输入

### 2.1 setup 家族和 statement 身份

在标量域 F_p 上，`p=21888242871839275222246405745257275088548364400416034343698204186575808495617`。共同 setup 变量是 X、alpha、beta；三个独立变量为 Delta_g、Delta_t、Delta_l。它们分别属于当前 genesis、当前 transition、历史 genesis key。各 key 的 gamma=1。

密码学 statement 记为 `(key_namespace, logical_relation, ordered_signals)`，包括所用 CRS 身份。历史 genesis 的 logical relation 字符串虽相同，不能把它的模拟 proof 误作当前 key 的同 statement 例外。运行 authority 只选新 manifest 的两份 key；asset/config/context 绑定进一步防止旧 namespace 进入。将历史 key 纳入敌手的公开辅助输入不等于新增运行 API。

| key | n | 全部 wires | public（不含常数） | private-basis wires | H numerator 空间 |
| --- | ---: | ---: | ---: | ---: | --- |
| g | 2048 | 1762 | 5 | 1756 | t_g·Poly_(≤2047) |
| t | 16384 | 13254 | 25 | 13228 | t_t·Poly_(≤16382) ⊕ span{X^16383} |
| l | 2048 | 1762 | 5 | 1756 | 与 g 同一初始 QAP/H，独立 Delta_l |

private-basis wires 包括中间 witness wires，不与原 Circom private 输入的7/32项混淆。最终提取器返回完整 R1CS assignment，再投影到规范源 witness。

### 2.2 typed opaque generic 模型

敌手只通过已登记的 G1/G2/GT handles 运算。源群加、取负和已知 F_p scalar 乘是线性运算；pairing 只接受 G1×G2；GT 允许乘、逆和已知 scalar 幂，没有 GT→G1/G2 的映射。相同群元素具有相同 opaque encoding；不同形式表达式偶然求值相同计入§7。不能把真实曲线坐标的任意算术能力悄悄算在这个定理内。

额外 source sampling/import 只允许：新的独立均匀指数 Z 的点，或已有 handles 的已知 scalar 组合。一个采样点 degree=1；实际 setup 贡献的 Z·X、Z·alpha、Z·beta、Z·Delta PoK 点 degree=2。不得由“新点”接口给出与 trapdoor 相关但未列出的逆查询。所有 setup-dependent 辅助群元素必须在下面的完整 source 基底中有表示。

除群 oracle 外，敌手可运行任意已知 scalar/字节算法、签名、HPKE 和独立其他群算法，可以把群 encoding 作为 hash 输入并自适应选择 signals/scalars。setup hash/source oracle 与 native R_1…R_7 是独立、一致、域分离的表。固定 symbolic transcript 的独立 encoding 标签、敌手随机币、外部输入和 oracle 答复后，这些选择是已知 field coefficients，而不是 alpha/beta/Delta 的离散对数。允许 native RO 编程；不允许某个未列 oracle 返回 pairing-trapdoor 的相关指数。

静态恶意 owner 完全拥有自己的签名密钥。不存在给恶意 key 无 witness 模拟 proof 的服务。自适应腐化、诚实 owner 任意改签服务、泄露旧 trapdoor/seed 都不在实验内。

### 2.3 SimSetup 与固定资产的解释

SimSetup 按同一正确 setup 分布创建公开 CRS/manifest/config 身份，保留仅供 reduction 的 trapdoor；在诚实输入前固定，此后不换 key。本文没有从已有公开字节恢复 trapdoor 的算法，运行 authority 不因此获得 trapdoor。

固定 development 文件的实例结论以其来自正确独立采样、陷门未知为前提。源码、贡献关系和 SHA 可核验；熵、擦除、泄露与主机安全没有被文件比对认证。这个条件不是一个未经证明但被填成零的 epsilon。若改变 setup 信任域，需要新 theorem/ceremony，不能只调整 budget 数值。

## 3. 全部公开 source 基底及精确数量

### 3.1 基底类型

记 `q_(r,i)=beta*u_(r,i)(X)+alpha*v_(r,i)(X)+w_(r,i)(X)`，`t_r=X^n_r−1`。

| 来源 | G1 指数 | G2 指数 | 最大总 degree（未乘共同分母） |
| --- | --- | --- | ---: |
| raw phase1 | X^i（i≤32766）、alpha X^i、beta X^i（i≤16383） | X^i（i≤16383）、beta | G1 32766；G2 16383 |
| prepared phase1 | 上述多项式的公开线性组合；顶层缺失幂补零 | 上述 G2 的公开线性组合 | 不增加 degree |
| initial zkey | alpha、beta、1、u_i、v_i、q_i、实际 H numerator | beta、1、v_i | 至多 raw/实际 H degree |
| final zkey | alpha、beta、Delta_r、u_i、v_i；private q_i/Delta_r；K/Delta_r | beta、1、Delta_r、v_i | 只有单个 Delta_r 的负一次幂 |
| phase1 PoK | kappa_x、kappa_x X；kappa_a、kappa_a alpha；kappa_b、kappa_b beta | eta_x X、eta_a alpha、eta_b beta；对应 source eta 可重建 | 2 |
| 每个 phase2 PoK | kappa_r、kappa_r Delta_r、Delta_r | eta_r Delta_r；source eta_r 可重建 | 2 |
| vkey GT | — | — | alpha beta，degree2 |
| 新独立 source 点 | 新 Z_1 | 新 Z_2 | 1 |

不存在 public q_i/Delta_r 查询。public q_i=IC_i 因 gamma=1 而无分母；这一区分对提取必需。不得因两类点都出现在 zkey 就混淆。

### 3.2 全部 serialized slots 的保守 handle 上界

下表逐 section 读取。相同点的重复槽位仍全部计入，因而是敌手初始 distinct handles 的可审上界，不依赖高成本逐点去重：

| 文件/来源 | G1 slots | G2 slots | GT slots |
| --- | ---: | ---: | ---: |
| prepared ptau（含 raw、prepared、1项贡献） | 196613 | 49157 | 0 |
| 当前 genesis initial | 7337 | 1765 | 0 |
| 当前 genesis final | 7340 | 1766 | 0 |
| 当前 transition initial | 56149 | 13257 | 0 |
| 当前 transition final | 56152 | 13258 | 0 |
| 历史 genesis final | 7340 | 1766 | 0 |
| 三份 vkey JSON 合计 | 41 | 9 | 3 |
| 可重建 hash-to-G2 sources | 0 | 6 | 0 |
| 每群 identity/generator | 2 | 2 | 2 |
| **N10,N20,NT0** | **330974** | **80986** | **5** |

ptau 的 G1 raw 数为32767+16384+16384，prepared 数为65535+32767+32767，再加贡献9点；G2 为16384+1+32767，再加贡献5点。每份 zkey header 有3个G1、3个G2；其 sections3/5/6/7/8/9 逐项计 public IC/A/B1/B2/private/H，每个 phase2 transcript 另有3个G1与1个G2。

**历史文件闭包。** 机械检查确认旧 phase2.ptau、genesis initial、两份 R1CS 与新副本 SHA 相等；旧 contributed.ptau 的 raw sections2–7 已逐字节包含于 prepared.ptau；初始 pot 的每一个点均为已知 generator。失败的旧 transition initial 只有252B，精确等于当前 initial key 的文件前缀，仅含现有 alpha1/beta1 header 点，没有新 delta 或逆查询。公开 copies 没有增加 setup 变量，不重复生成 independent source。额外历史 final genesis 却不同，故确实加入第三 delta 和对应贡献/source。

初稿枚举保存在 budget-audit-001.json [source omitted from this derivative]，增加共享header/历史ABC及反例控制后的记录为 budget-audit-002.json [source omitted from this derivative]，最终合同与真实source补证记录为 budget-audit-003.json [source omitted from this derivative]。旧输出均保留原SHA，不因脚本增强而覆盖。没有读取 client-private、owner key 或 witness。未来若又公开相关 final key/中间贡献，必须重列 source，不能继续沿用 k=3。

## 4. 编译关系的 Q/H 引理

**Lemma Q。** 三个 key 的 public u 独立且与 private u 张成空间零交。g/t 的实际 zkey 在原 constraints 后追加包含常数的6/26个 A-only 单位行，B=C=0；l 与 g 的初始关系字节相同。在第 j 个新增域根 z_j 上，u_i(z_j)=1_(i=j)，所有 private u(z_j)=0；对等式求值逐一杀 public 系数，立即得独立和零交。没有假设其他 public v/w 也独立。

**Lemma H。** 每个目标 QAP residual R=UV−W 若属于实际 H numerator span，则 R=tH_std，deg H_std≤n−2。

完整2n odd-Lagrange 点的 span 是 `t·Poly_(≤n−1)`。g/l 在可用 power 范围内，R 的 degree≤2n−2，杀掉候选的2n−1最高项。t 的 phase1 已达容量，最高 tau^(2n−1) 补零使实际空间为 `t·Poly_(≤n−2)⊕span{X^(n−1)}`；在任一新增 A-only 域根上 B=C=0，故 R(z)=0，t(z)=0而 z^(n−1)≠0，额外方向系数必为0。这是精确空间而非从点数猜测 divisibility。

冻结的 QAP/H 检查已核对32个单位行、18432个 initial H 点与 prepared odd-Lagrange 字节。历史 g 的 byte equality 将该结论带到 l。正确 phase2 将相同私有/H numerator 除以独立 Delta_r，属于 setup 实现前提。

## 5. 完整白盒 weak-SE 定理

### 5.1 正规表示与自适应查询

给每个 key 的第i次外部 source 调用（真实或模拟）登记独立 `mu_i,nu_i←F_p`，返回

`([mu_i]_1,[nu_i]_2,[S_i]_1)`，其中

`S_i=(mu_i nu_i−alpha beta−Q_r(phi_i))/Delta_r`，

`Q_r(phi)=Σ_public phi_j q_(r,j)`，phi_0=1。完整 `(key,relation,phi_i)` 必须在本次新 mu_i/nu_i 抽样前已确定；它可依赖所有过去 proof、native messages、RO 和错误。重复 statement 但 fresh proof 仍是新索引，S_g/S_t/S_l 各加1；缓存原字节不加。

**真实 source proof 同样需要登记。** 对真实statement及其任意真实witness，`mu=A_exp=alpha+U+r Delta`、`nu=B_exp=beta+V+s Delta`；因Delta非零且r/s全域均匀，这是给定过去与setup后的双射，mu/nu与setup独立均匀，C正是S_i公式。因此外部诚实真实proof与模拟proof共用上述source表示，不需要extractor知道mu/nu数值或诚实witness；所有fresh外部真实proof也计S并登记其真实来源/statement。若proof完全由敌手的已知scalar/witness与generic运算产生，白盒日志已将其展开在CRS基底中，可以不建独立source索引，但其运算/输出必须进入Q。只有这一完整展开情形才允许C实验的S=0；不能从“运行未用模拟proof”直接推S=0。若source另按accepted-affine条件分布采样，使用§7.3相同条件分布或所列耦合项。

在 symbolic generic 执行里，令 R=F_p[X,Z]，alpha、beta、Delta、mu/nu 为其余形式变量。任何源群输出有已知 scalar 系数表示

```
A = alpha*a + beta*b + P + Σ c_r Delta_r
    + Σ E_r/Delta_r + Σ a_i mu_i + Σ b_i S_i
E_r = beta U_(r,e) + alpha V_(r,e) + W_(r,e) + K_r
B = alpha*h + beta*f + Q + Σ g_r Delta_r + Σ z_i nu_i .
```

C 与 A 同形，系数用帽号。e 是 private queries 的已知 scalar 组合，K 属于实际 H 空间。a,b,P,c_r,h,f,Q,g_r 位于实际 source 产生的 R 子空间；允许把它们放大到 R 做形式比较，但§6的 degree 只按实际基底闭包计算，不把任意高次 R 多项式凭空交给敌手。G1 没有独立 nu_i，G2 没有 mu_i、S_i 或负 Delta。

目标 key j 接受意味着 `AB=alpha beta+Q_j(phi)+Delta_j C`。形式不等而实际接受的唯一 generic 情况计入§7；下面在无该坏事件时逐项证明。

### 5.2 A 中模拟 S 项不可能

若某 b_i≠0，mu_i nu_i nu_l 项给 b_i z_l=0，故所有 z_l=0。mu_i nu_i 项再给 `b_i B_0=Delta_j b_hat_i`；b_i、b_hat_i 是 scalar，B_0 必为目标 Delta_j 的 scalar 倍。将 A/C 的成对 S 项相消后，剩余项乘 Delta_j 没有 delta 无关 alpha beta 项，右侧却保留系数1，矛盾。因此所有 b_i=0。

### 5.3 模拟元素分支恰为同 key、同 statement

若只有 A 用 mu，独立 nu 项先杀 C 的 S，mu 项使 B 为 Delta_j scalar 倍，仍缺 alpha beta，矛盾。若只有 B 用 nu，独立 nu 项直接杀 A；其余方程仍不可能。因此真模拟分支必有 a_i z_i≠0。

对角外 mu_i nu_l（i≠l）使 a_i z_l=0；只剩唯一同索引。对角项为

`a_i z_i=(Delta_j/Delta_r)b_hat_i`。

scalar 左边非零且各 Delta 独立，故 r=j；共享 X/alpha/beta 无影响。单独 nu 给 A_core=0；单独 mu 给 B_core 为 Delta_j scalar 倍；alpha beta 项给 a_i z_i=b_hat_i=1。剩余 `Q_j(phi−phi_i)+Delta_j C_core=0`。逐个 foreign Delta_j/Delta_r 项及正 Delta 项消去不相关部分后，beta 系数为 public u 差与 target private u 组合相抵。Lemma Q 迫使 phi=phi_i。

于是 extractor 可指认完全相同的已登记 source statement，包括 key namespace；对模拟来源保留 weak-SE 例外，真实来源则复用其真实语义或已知 witness，不对其重随机 proof 额外承诺提取 witness。历史 key 的同数字 signals 不构成当前 key 的例外。

### 5.4 无模拟分支：两个方向都可提取

无 A/B 模拟项时，mu/nu 比较亦杀 C 的模拟项。无 Delta 的 alpha²、beta²、alpha beta 项为

`ah=0, bf=0, af+bh=1`。

R 是整环，其 units 只有 F_p*。因此有且只有以下两类：

**方向I：a≠0。** h=0，af=1使a,f为非零常数，b=0。负 Delta 的 alpha beta、beta²、beta 项逐一给 V_(r,e)=U_(r,e)=W_(r,e)+K_r=0，故 A 的所有分母消失。foreign beta Delta_r、alpha Delta_r 又杀 c_r,g_r；C 的 foreign Delta_j/Delta_r 项被唯一来源比较消去。余下

`fP=U_(j,phi)+U_(j,e_hat)`，

`Q/f=V_(j,phi)+V_(j,e_hat)`，

`PQ=W_(j,phi)+W_(j,e_hat)+K_hat_j`。

**方向II：a=0。** bh=1使b,h为非零常数，f=0。负 Delta 的 alpha beta、alpha²、alpha 项同样杀 A 所有 E_r；foreign delta 与 C 的 foreign 分母同样消去。此时

`bQ=U_(j,phi)+U_(j,e_hat)`，

`P/b=V_(j,phi)+V_(j,e_hat)`，

`PQ=W_(j,phi)+W_(j,e_hat)+K_hat_j`。

两方向都得 `U_(phi,e_hat)V_(phi,e_hat)−W_(phi,e_hat)=K_hat_j`。此时才用 Lemma H 恢复标准 tH/divisibility，给完整满足 R1CS 的已知 private scalar vector e_hat。无需离散对数、未知 opening oracle 或恶意 owner 诚实性。

G4a 使用 actual h 空间无unit排除方向II；这里补全它，使已知scalar倍 alpha_G2 的扩展本身也不构成伪造。仍不能把 G2 中含 alpha²、alpha beta、相关逆等未知新基底自动纳入这个表示。

### 5.5 定理及在线提取

**Theorem E。** 在§2–4的实验里，对任意有限自适应执行，存在维护 generic 线性表示日志的白盒在线提取器。除§7的一次全执行坏事件，每个接受 proof 或输出其 key 的 R1CS witness，或指认该 key 的 exact registered source statement（真实或模拟）。将 source 全取模拟调用即得 white-box weak-SE；允许真实 source 的扩展由§5.1的精确重参数化给出。提取器不 rewind，不重抽 RO/setup，不解密 honest HPKE challenge，也不把 owner 签名当 knowledge。

证明为§5.2–5.4的穷尽分支。已知 scalar 线性表示随每次源群运算更新；多个形式相同的表示任选其一；若形式不同但实际编码相同，计一次全执行 generic collision。一次坏事件可覆盖所有输出，不再按每个 accepted proof 重乘其概率。

## 6. 显式 degree：为什么不是 O()、也不随 S 线性增长

共同分母 `D=Delta_g Delta_t Delta_l`，总 degree3。任何 G1 表达式只有各个 Delta 的一次逆，任意多个模拟 proof 的**线性**组合亦然；不能错误地给每次模拟查询再乘一个分母。

| 表达式 | 乘 D 后的最大总 degree |
| --- | ---: |
| 最大 raw G1 power X^32766 | 32766+3=32769 |
| alpha/beta·X^16383 | 16384+3=16387 |
| transition H/Delta_t | 32766+2=32768 |
| genesis g/l H/Delta_r | 4095+2=4097 |
| private q_i/Delta_r | 16384+2=16386 |
| 任一模拟 S_i | max(2,n_r)+2≤16386 |
| 新独立 Z 或 PoK Z·trapdoor | ≤2+3=5 |

所以 **D1=32769**。G2 无分母，最大 raw X^16383，故 **D2=16383**。GT 的源是一次 G1×G2，再作已知scalar线性组合；乘 D 后 degree 至多 **DT=D1+D2=49152**。验证式的 Delta_j C 项至多 D1+1=32770，Q_j 项至多16384+3=16387，alpha beta 项5，均被DT覆盖。

S_g/S_t/S_l 每次引入新的 mu_i、nu_i 变量和两个G1/一个G2输出，但 S_i 分子的最高 degree 仍是 max(2,n_r)。所有 extra independent source 点也只引入 degree1新变量。因而它们增加 handles 和变量数量，不增加上述 degree。

对将来扩展，若合法的无分母 source 最高 degree变成L1/L2，private/H/simulation numerator最高为M，则

`D1'=max(L1+k,M+k−1)`，`D2'=L2`，

`DT'=max(D1'+L2,D1'+1,max_r n_r+k,2+k)`。

这是 degree 规则，**不是**提取条件的自动放行。新source还须满足§5正规表示/public-private划分。尤其把public q_i/Delta_r也公开，虽然 degree 不超过M，却允许下节的直接statement malleation。

## 7. 泛型碰撞与 setup/affine 的精确界

### 7.1 条件化 Schwartz–Zippel，不隐藏常数

默认全域source采样下，X 在 `F_p\({0}∪μ_16384)` 上均匀，大小 `p−16385`；因为2048整除16384，g/l域包含于该根集合。alpha、beta、三个 Delta 在F_p*均匀；Z、mu、nu在F_p均匀；变量相互独立。§7.3另给逐query局部accepted-affine采样的精确扩展。

对变量分别来自有限集合、最小集合大小M的非零总degree≤d多项式，逐最后变量展开并按最高项归纳：若该最高系数不为0，最后变量至多其单变量degree个根；最高系数为0的概率再由其余变量degree归纳，二项和≤d/M。这里M=p−16385。清掉D不改变好采样域上的零集合，因为每个Delta非零。

同一归纳还允许**按prefix选择均匀采样域**：第k个变量给定此前变量后，均匀取自某个大小至少M的集合，之后的抽样不重新加权此前prefix。将非零多项式写成最后变量的s次式，其最高非零系数的总degree≤d−s；归纳给该系数为零的概率≤(d−s)/M，否则最后变量条件命中根的概率≤s/M。两项相加仍≤d/M。这个证明不需要集合彼此独立；它不适用于把完整transcript一次性条件化后任意倾斜setup/prefix的分布。

在 symbolic oracle 中预先给形式不同的表达式独立encoding标签，并回答形式相同的表达式相同标签。其所有已知scalar选择可先固定，再独立采样setup/source/simulation指数。第一次实际碰撞前，它与真实generic执行一致；故对全部已生成表达式对做union bound即覆盖自适应分支、显式equals、隐式encoding相等和每个验证结果。相同多项式的配对不计坏事件，但用全部槽位对上界仍合法。

令 H1,H2,HT 是各群整个执行的handle数上界。则

`epsilon_collision ≤ min(1, [32769·H1(H1−1)/2 + 16383·H2(H2−1)/2 + 49152·HT(HT−1)/2] / (p−16385))`。   (B)

没有未知常数或每次错误相互独立假设。多次比较同一已有表达式对无需另乘测试次数；若测试形成新表达式/验证残差，必须将相应输出登记进handles。

### 7.2 精确 handle 账本

所有变量为事前有限非负整数公开上限，不声称运行source强制执行。S=S_g+S_t+S_l 包含§5.1的所有fresh外部真实/模拟source，V=V_g+V_t+V_l。Q1/Q2/QT/Qpair 只记额外oracle输出，排除以下单列source/validator成本；I1/I2记额外source采样/import。若选择完全内联某真实proof，必须把其全部generic生成工作计Q，不能同时省S和Q。

```
H1 = 330974 + 2S + Q1 + I1 + 13V_g + 53V_t + 13V_l
H2 =  80986 +  S + Q2 + I2 + V
HT =      5 + Qpair + QT + 7V .
```

对ell项public的真实verify：ell次scalar乘，ell−1次sum加，1次IC0加，1次neg A；新guard再有A/C两个完整整数scalar乘，合计2ell+3个G1输出。B guard有1个G2输出；四对pairing与三次GT乘共7输出。多项式阶不因实现用MSM或批量pairing而变化；此处是抽象oracle上界，不是CPU性能计数。

V包括被拒尝试；genesis exact HTTP retry仍重新验proof。transition的8次持久attempt限制仅用于实际该API/RID；公共离线pairing、genesis或额外oracle工作不能从此消失。对手PPT时间上限可给Q/S/V上界，但“PPT”本身不是一个现成数值。不得把功能run的有限verify数量冒充对手预算。

### 7.3 setup sampling 与 ZK/affine

若最初X/alpha/beta/三个Delta从整个F_p独立均匀采样，好setup的概率为

`[(p−16385)/p]·[(p−1)/p]^5`。

故 `epsilon_setup_sampling=1−[(p−16385)/p]·[(p−1)/p]^5≤16390/p`。若setup定义直接条件化于上述好域，则本项为0。它只数零值/域根采样，不数有毒废料泄露或未知真实熵；后两者是实验前提失败，不给虚构数值。

给定任意statement与好setup，真实Groth16的独立全域r/s使A、B的指数独立均匀；C由验证式唯一决定。式S_i产生精确相同分布。因此自适应多次真实statement ZK通过逐条件分布归纳是完美的，不另给“多定理ZK ε”未知常数。

运行schema排除A/B/C为identity。令c=alpha beta+Q(phi)。若c=0，则任一identity事件就是A=0或B=0，质量(2p−1)/p²；若c≠0，AB=c与A=0或B=0不相交，质量(3p−2)/p²。因此至多S次fresh source proof耦合可用

`epsilon_affine≤min(1,S(3p−2)/p²)`，

比冻结G4a的4S/p保守界更紧。默认根账本保留此项，不假设runtime隐藏重采样。

可选的零affine项需要一个明确的source oracle：给定每次已固定statement与过去prefix，在**本query内部**把真实Prove和Sim都采样至A/B/C非identity，失败次数不暴露，且不重抽setup或过去proof。此分布可精确写成先取`mu←F_p*`；当c=0时取`nu←F_p*`，当c≠0时取`nu←F_p*\{c/mu}`。每个非零mu恰有p−1或p−2个可用nu，故它就是全域mu/nu对在本query接受条件下的均匀分布，且real/sim仍完全一致。依§7.1的prefix归纳，所有条件域大小仍≥p−16385，式(B)不变，提取的形式恒等式也不变。因此只有在这项额外的逐query采样/可观察性约定下才能取epsilon_affine=0；不能只由“ZK两边相同”省略提取的碰撞论证。有限实现若暴露失败、内部重试耗时或截断，则须按实际可见流及其耗尽概率另计；本实例的默认式继续使用上面的S(3p−2)/p²。

单执行/单世界最终接口为

`epsilon_G16|good_setup = min(1,epsilon_collision+epsilon_affine)`，

`epsilon_G16 = min(1,epsilon_setup_sampling+epsilon_collision+epsilon_affine)`。

若根组合对两个世界/多个hybrid端点各用一次此实验，可逐项相加；每个端点使用覆盖其真实/模拟sources的同一公开caps，但互斥端点并非现实中同时出现的handles。根账本选 `M=2(C_HPKE+10)` 后，连同setup sampling、collision、affine逐端点保守union是合法上界，无需主张一次mastercoupling。不能既在单端G16项内计一次collision，又按每个acceptedproof重加同一collision。式(B)保留source与identity的配对，本已覆盖其identity坏事件；另加affine是保守冗余，不能因此误称两项统计独立。HPKE、哈希、签名、native/FLP、nonce由根账本分别计，不在本式重复。

## 8. owner、origin、HPKE 与全前缀的完整接口

### 8.1 H/W/E 路由及反例

完整source查询表记录所有S调用；H表收录其中honest-source真实或模拟调用的完整key/statement/body/packet/semantic handle，W表仅收录事前已知witness的来源，E表缓存新statement成功提取结果。任何相关历史sourceproof也必须计入S并登记，不能当不受限的setup-correlatedauxiliary输入。若一个扩展API按已知witness为W产生fresh外部proof，同样登记source并计S；恶意owner自己已知scalar生成的proof只在完整日志展开时改计Q。

背景prelude另登记F类：由可信真实随机化Prove或Sim产生、但属于foreign key/task/config/asset/epoch的source proof。它仍计S；若key不同，§5.3不允许跨Delta借其例外；若key相同而业务上下文不同，真实metadata/context检查拒绝，除已列hash/认证坏事件。不能因为历史文件公开就把它们一律放H。任意恶意算法生成的背景proof须连其generic生成过程计Q，或满足已声明的独立import规则，不能仅因通过pairing而当成独立随机source。

source API因此有明确可检验的边界：当前接纳namespace的外部source只能是静态保护的H或已知witness的W。若另允许恶意owner在当前namespace得到一个未知witness的外部真实proof，再自签新BODY，Theorem E仍只给同source例外，wrapper不能声称已提取其坐标；必须提供其可信语义/已知witness，或改变实验/构造。这与无witness模拟API反例同属不能省略的辅助输入限制，不由owner签名修复。

对不在H/W/E的接受proof，用Theorem E；对W/E复用witness。对H的同statement，context重算、完整orderedsignals、域分离长度前缀和package digest共同固定owner/uid/epoch/task/config/assets/window/step/RID与整个raw report/两sidecar，除哈希碰撞。只改proof会改BODY/body_id；honest owner没有任意改签API，恶意owner自己签名不算伪造。

context的两个128-bit limbs合起来保留完整256-bit SHA结果；不是两个各自独立的128-bit碰撞假设。context/package/BODY等统一交给根账本对同一域分离SHA256函数的总碰撞优势，本文不重复乘域数或为每个limb另收费。

**不可删除的反例。** 给恶意owner一个它自己statement的无witness模拟proof，它可公开重随机并自签新BODY；无签名伪造且weak-SE不要求提取。这说明W/H规则不是形式记账，而是必须由现有API/静态腐化模型保证；不能用“owner签名有效”替代它。

### 8.2 HPKE 标签与合法解密路由

精确challenge tuple为 `(recipient key handle,suite,info,AAD,enc,payload)`。native AAD含task、metadata(RID,timestamp)、public_share；sidecar AAD含task、RID、config、raw digest、role、core digest。core本身不含owner，故不能只靠core防跨owner搬运。

诚实source在packet首次公开前已持久获得唯一RID的OriginCert。authority先验rawRID=envelopeRID、owner签名、OriginCert全部身份/slot/RID字段与已预留证书一致；origins.report_id全task唯一。configured/fenced native入口先核完整body/permit及精确收到的raw/subset，再解密。

由此：同H完整packet走其一次semantic handle/journal/cache；同statement改包是context/package碰撞；新statement先提取/复用witness再继续逐密文处理；复制原challenge tuple到另一owner需同RID而被origin唯一性或honest新BODY签名阻断；改RID/AAD/info/recipient或ciphertext则是合法不同CCA tuple，返回plaintext或拒绝后运行真实算法。不预先假设任意恶意密文字节的明文已知。诚实RID公开前被抢占/猜中只计诚实nonce事件，恶意自选RID不套生日界。

相邻固定世界HPKE混合知道原始挑战m0；对标记H来源使用其原semantic handle，bit0与真实解密相同，bit1明确sourceoverride，而不是让真实role解dummy仍自动成功。非H永远按合法decryptoracle/自有key真实处理。最终nativeRO/FLP与receipt公式接管H，从而消除m0。改变digest/context/proof/signature均在该报告首次公开前整体构造；不修改已交付/持久body。

本文件只对§2 generic transcript作在线提取，不需要HPKE challenge私钥，也不rewind/重编已经回答的nativeRO。完整逐密文/CT/HPKE primitive前提和source route在冻结G4a03§7.1–7.2；G4b原生证明沿用该明确接口，不假设“目标组合已安全”。

### 8.3 非H恶意报告不能借P的完整性

P/P+A允许恶意owner与腐化role串谋。W4 witness只给声明桶x_j/承诺opening，不给nativecipherplaintext，也不强迫其实际native输出一热。非H的实际honest retained output w_h,j由合法解密和真实native执行可计算；H才有identity关系 `v_h,i=e_(I_i)−v_c,i^orig`。

完整R首次允许暴露时，仅用一次含sentinel的授权声明总和O_C(R)，生成

`V_h,R=O_C(R)−Σ_(j∈R\H)e_(x_j)−Σ_(i∈R∩H)v_c,i^orig+Σ_(j∈R\H)w_h,j`。

代入O_C的声明总和后即为双方分类的实际honest份额和；不要求非H的两份相加为e_x。删sentinel接口先用公开b恢复其count。非H失败/无retained则不能通过完整R门。exactretry不新增source/randomness或输出；错误/verdict由本次模拟状态计算，不给个体histogram或秘密verdict额外oracle。A的零输出模拟器不使用O_C。

## 9. 模型扩展的实质反例与检查边界

若额外公开public `q_i/Delta_j`，给一个真实statement phi的合法proof后，任何新phi'可令

`C'=C+Σ_public(phi_i−phi'_i)[q_i/Delta_j]_1`，A/B不变，

从而验证方程保持。这些额外点的degree并不大，故只通过degree测试不能证明提取。例：一个无private输入的R1CS用原行 `x·1=0`，另加public A-only单位行；x=0为真、x=1为假，新增public逆查询允许上述proof搬运。实际冻结source没有这些逆查询；本例不声称实际profile已有forge。

相反，新增纯alpha_G2本身不构成反例，因为§5.4方向II给出了完整补证。任意on-curve非prime G2也不是自动forge：冻结G4a保留的optimal-ate标准投影反例只证明不能靠投影补输入域；新guard将实际acceptedproof限制在prime domain。

首次只读审计已退出0，枚举/历史闭包/精确有理数/degree/低degree额外逆查询反例全部检查相符。脚本是支持性算术和字节核验；§4–8的形式证明不能由机械“all_passed”替代。它没有运行prover/native、生成key或修改旧结果，也没有进入G5/G6。冻结G4a保持原SHA。

## 10. 本次检查记录与稳定交付

最终 audit_budget.py [source omitted from this derivative] 只读重算：完整source槽位与历史副本闭包；五key共享alpha/beta/gamma header、历史genesis的ABC与当前相同且delta点不同；degree从实际section长度推导；合同表达式与独立手算H1/H2/HT及collision相等；F_7穷举12个允许系数分支；F_101穷举10201对真实proof币验证mu/nu双射与C公式；遍历全部101个c、每个10201对A/B核对affine质量，并逐mu核对局部条件采样域的等大小性。delta点不同不被冒称独立随机性认证。最终检查另存 budget-audit-004.json [source omitted from this derivative]，不覆盖001–003。

`budget-contract.json` 的示例公开caps是S_g=S_t=V_g=V_t=2^19、S_l=V_l=0，Q1=Q2=QT=Qpair=2^40，I1=I2=2^20。精确有理数算术验证该示例单端epsilon_G16<2^-150；这是所列generic模型中的算术演示，不是当前runtime资源enforcement、整系统位数或性能测量。根组合的HPKE/native/signature/Com等优势及端点数必须另加。

初次读取旧252B失败key的通用section解析报struct.error，随后按partialheader字节检查确认它与已列key前缀完全相等；没有删去该失败文件或伪装成完整key。一次补文apply_patch因上下文前缀不匹配而未落盘，按真实行重试成功；另一次空patch同样未落盘。它们是读取/编辑调用错误，均未改变任何冻结输入。命令/失败分类及保留run身份见 execution-record.json [source omitted from this derivative]。

W4局部交付只签本文件所证的conditional theorem与显式账本。完整G4b由根任务合成、独立全文审读及最终checker后验收；本任务不创建acceptance、不改Gate/Obsidian，不以此先行签整体通过。
