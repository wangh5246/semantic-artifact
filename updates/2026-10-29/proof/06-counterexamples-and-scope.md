# G4b：守卫反例、适用范围与负控制

日期：2026-10-18。所有反例均给出被删除的守卫或被越界推广的命题；不是声称冻结新G4a源码含相应攻击。本轮不改任何运行源、keys、G4a或G5冻结证据。执行命令与实际小模型输出在 sources/refinement [source omitted from this derivative]，精确边界见[05](05-closure-prefix-and-refinement.md)。

## 1. 等量histogram下，首曝后检查不能挽回隐私

令D=10000，完整R有八条eligible记录，两合法世界依次为

`H0=(1,2,3,4,5,6,D,D)`，`H1=(2,1,3,4,5,6,D,D)`。

完整histogram相同，公开b=(1,1,1,1,1,1,0,0)相同；每owner可取恒定合法坐标，具有独立合法genesis、相同公开拓扑。若删除“**任何首次share前**完整R reservation”守卫，trace为：lock完整R→只完成/选择R\{第一条}→先发诚实share→腐化role/Collector用对应份额重建子集histogram→最后publication拒绝。H0的该子集缺桶1，H1缺桶2，故区分；最后拒绝不收回泄漏。脚本直接重算两个完整及子集histogram。B_min、最终总和相同或后续abort都不能修复该trace。

正模型要求所有fresh/cache出口同样reserve；把缓存当无须检查会重复出现同trace。部分R在准备阶段留下孤立retained不等同允许导出它。

## 2. 只比eligible、count或RID不够

P={独立warmup w、eligible a、eligible zero z}，R={a,z}。trace：锁P→只commit/apply a,z→A=M=R成立→若省略L=P则导出，w仍未commit，违反完整登记锁合同。w属于另一uid，其未完成不被a/z的历史依赖自动覆盖；不能只挑让fullR恰巧蕴含fullP的fixture说明守卫冗余。

完整记录另含body/statement/context、next/prev/K、owner/window/config等。给相同RID/条数但把body或next commitment换成另一值的映射，RID集合和count仍相等，完整P/L/M关系不同。即使native count+RID checksum一致，也没有证明实际share来自认证body的retained session；必须重新核定完整记录与私有retained link。

zero z是e_D，不能从R或consumed membership删掉；删掉它后应用层可见正histogram可能相同，但完整report_count、R root、资格和原生有效域已改变。warmup APPLIED也不是eligible membership的证据。

## 3. 真head/K、quota与持久化负例

**兄弟并发。** 同uid原head=h、version=v；候选a,b都引用h。若从事务外检查通过后不做实际head/version CAS，两事务分别追加a和b、各自扣一份quota，形成两个成功后继。若commit了a又abort时回退head/quota，下一窗口可重复花费。正确实现只有一个CAS成功，abort保留prefix。

**替换K。** x坐标历史0..6为 `(0,0,0,0,0,0,3000)`，y恒0，全部步距和真实K约束合法。step7取x=6000：与prev距离平方9,000,000≤144,000,000，但真实K=step1的x=0，距离平方36,000,000>10,890,000。若把proof里的K任意换为x=6000的近点并不核真实history，proof局部anchor检查通过却不是实际ADWC历史；脚本核完前缀与下一步不等式。

**pending不是history。** register(a)→a原生失败未commit→若permit(b)接受pending a作为prev/K→b推进head。此时L包含b但缺依赖a，后继proof的局部关系不能补足真实接纳链。

**发送先于持久提交。** 计算snapshot→send→crash→事务未commit，恢复无journal/reservation→允许新分支/新payload。接收方已看到旧share，系统却记零暴露。正确顺序是commit→send；反向序列不是“概率很低的网络事故”，而是删除持久化前提的反例。

**跨库原子性幻觉。** authority commit与role apply是不同库。authority已commit→发送COMMIT网络丢失→role尚未apply是合法中间态；若凭authority已commit直接导出，M≠R。幂等恢复必须补投已存CommitCert，role在自身事务apply一次。不能用“outbox一定与所有role原子提交”作不存在的前提。

## 4. 唯一journal、重放与暴露单调

对Helper，删除同report/job/protected-step输入绑定可使：首次peer x提交response v；敌手改为x'再提交response v'。这不是exact retry，保存旧success却忽略请求变化也错误地把x'路由为x；正确Helper公开冲突，换job由report tombstone拦截。Leader使用不同机制：若删除同事务的lease expiry/token fence，旧worker与新worker可从同一旧state计算后各写不同transition，后写覆盖先写的已提交native状态/retained；正确实现使失去lease的整次写入回滚。

Leader提交前收到不同Helper回复而重算并非这个反例，也没有被声称全都公开冲突；固定原share、nonce/query/joint coins及已提交state的多次谓词可由03同一`Σ,z_h`精确模拟，全部物理调用计预算。小模型的no-journal事件只表示**第二个已提交分支**，不是检验提交前CPU只运行一次。

若删除apply幂等：commit→merge share once→reply lost→同CommitCert retry→第二次merge，count/histogram加倍。不能因为membership表的 `ON CONFLICT DO NOTHING` 便忽略此前已重复执行的batch加法；正确代码在merge之前查exact旧commit，并把merge/status/member/commit同事务提交。

若删除payload唯一性：同E先发Z，重试计算Z'仍引用E，snapshot identity相同却增加一次数值查询。只缓存随机snapshot_id不能证明plaintext相同。若snapshot不耐crash，send后重启能忘掉它；若collect失败把暴露清零，再换R'则产生二次查询。`EXPOSURE_UNKNOWN_COLLECTION_FAILED`不能当作PRE，send intent可保守高估，不能假造实际已交付确认。

## 5. Moment有效域和恶意role完整性越界

一般向量中 `F(e_0+e_2)=F(2e_1)=2`，两者向量总和亦都为2；moment不是通用向量承诺。零向量和e_0同moment0；SumVec多1并非Histogram合法一热。只有逐报告重建保证e_y、0≤y≤D<q时，F(e_y)=y才单射。扩大桶到q还会使e_0与e_q模q相同。

声明bucket23而实际valid native bucket107；恶意role自持签名key，可在看到诚实receipt m_h后选择 `m'_c=T−m_h`，所以authority equation通过，实际reconstruction仍可能e_107。脚本给T=1023、m_h=700、m'_c=323的具体field算术。合法签名只说明该role说过这个值，不能证明它诚实从原output算出；C要求两个正确roles，P允许该行为且只保证隐私/诚实share集合界。

在P/P+A混合R里，非H malicious-owner记录也可能被主动peer帮助通过native preparation，实际output不是声明e_x。若错误用 `O_C−Σ_R v_c^orig` 合成honest aggregate，就偷用了C完整性。正确式为05§6的H/non-H分解；non-H实际honest output由合法解密和真实算法已知，而非想当然一热。

另一种不能暗中扩大的是C对手知道native verification key。它可对自选RID先算query r，再选择在这个r满足的伪造proof。具体对非法全零Histogram，sum-check S=−1；令声称的gadget多项式P恒为k=b/101，则第一项 `b·101k−b²=0`。对任意非root r，seed节点的Lagrange系数λ_0(r)非零，恶意prover可反求200个seed值，使query的wire求值为 `(1,k,0,…,0)`，从而gadget检查也等于P(r)。P虽未诚实表示真实range计算，单个已知r的核验仍通过。标准C要求随机key对客户端隐藏；P腐化role知key而不承诺完整性，二者不矛盾。F17小模型 [source omitted from this derivative] 给出calls=2的实际λ/seed/非法输入验证等式；没有运行新native攻击。

## 6. Weak-SE、origin和HPKE禁查询

weak白盒SE只对不是模拟查询的**新statement**提取。若给自持key的恶意owner一个未知witness statement的模拟proof，它可重随机后自己签新BODY；签名合法，也无须触发新statement提取。满域Pedersen opening“存在”不代表能算出。脚本仅用F_101中的配对指数方程检查公开重随机恒等式，false relation `w²=2` 无witness；这是说明接口逻辑的toy，不是现实Groth16 forge。

新实例使用H（honest模拟来源）/W（先验已知witness）/E（新statement提取）区别。修改owner/uid/native package又想保持H exact statement会触发context/package hash绑定；保持honest身份但改proof/BODY需新honest签名。恶意owner自己的签名从不计为伪造。

HPKE解密挑战标记是 `(actual key,suite,info,AAD,enc,payload)`，不是短config id。若允许复用同挑战tuple到另一个恶意body、并让模拟器查询解密oracle，归约无效。真实native/sidecar AAD都含RID，honest OriginCert在packet公开前已经唯一占RID；另一owner不能取得同RID origin，冒用honest身份计认证坏事件。改RID/AAD则是合法不同tuple，必须用CCA oracle真实plaintext/bottom处理，不能凭“ciphertext看起来旧”一律拒绝。提取STATE/MASK witness也不代表native plaintext已知。

### 6.1 相关CRS与输入群域不能靠名称继承

额外公开目标relation的public `q_i/Delta` 查询时，同一A/B、任意新public statement phi'可取 `C'=C+Σ_public(phi_i−phi'_i)[q_i/Delta]_1`，保持验证方程。这些点的degree很低，因此仅检查degree上界不能代替提取的source基底条件。[02](02-groth16-extraction-and-budget.md)给出无private输入的 `x·1=0` 真/假statement toy及实际公开家族枚举：历史独立genesis final key是第三delta，不能漏计；公开copies/旧initial前缀则不应虚构为新的独立setup。单独新增alpha_G2本身不是forge，02对称方向II仍能提取。generic模型也没有自动变成原BKSV的AGM或现实任意曲线算法定理。

旧ffjavascript `G2.isValid`只检查on-curve；保留的公开投影诊断 [source omitted from this derivative]有on-curve非素子群Q，`[r]pi(Q)=0`、T=Q−pi(Q)非零且cofactor倍为0，但实际optimal-ate `e(g,Q)≠e(g,pi(Q))`、`e(g,T)≠1`。它否定任意输入的简单prime投影等价路线，没有给出满足完整Groth16方程的非法proof，不能写成已forge。新verifier在pairing前对A/B/C用完整整数 `[r]P=O` 收窄accepted域；若错误用先模r的timesFr，这项检查会恒为乘零，不能证明membership。

## 7. Context绑定：编码单射与哈希碰撞分别计算

完整SHA256 digest被拆为 `(hi128,lo128)`，每limb小于SNARK p，且 `digest=(hi<<128)|lo` 精确恢复。相同limbs因此必为同256bit digest；这里没有两个独立128bit hash，也没有额外mod p别名。字段/record的长度前缀、type tags、canonical整数、strict JSON键集合及顺序消除确定性编码歧义；如去掉长度前缀，`(ab,c)`与`(a,bc)`拼接相同，这属于codec缺陷而非SHA碰撞。

preimage不同且digest相同才进入SHA碰撞事件。BODY、package、context、record/P/R roots、request、journal、签名message等由同一SHA primitive组成，使用一个总查询/消息对预算或明确分项并集；domain分离不意味着独立primitive。禁止把一项循环依赖用“hash安全”跳过：context排除proof与自身limbs，包含所有其他signals及package身份，BODY另绑定proof及origin/packet，LockCert不塞回它所签body形成环。

固定96bit verification-key tag的编码属于ticket message，在当前事前固定task/key/config内；它不是对任意跨key选择、rotation或跨task复用的96bit唯一性证明。实际tag为`SHA256(verify_key)[:12]`，同时是secret key的相关泄漏，不能因为key本身未发送便直接套128bit key猜测。只知tag输出≤2^96种时，任意Q次猜测的无结构上界为`min(1,2^96 Q/2^128)`：对每种tag固定同一敌手/外部coins，各有至多Q个猜测key，再对tag分支并集。反例函数tag=key首96bits恰有32bit剩余支持；这说明SHA-CR不能自动认证隐藏key熵，不是声称已对实际SHA前缀实现32bit成本攻击。03/07明确放大C的keyguess项，并单独给新增普通SHA OW128假设下的更强corollary；不把CR当OW，也不把纯信息弱界写成实际攻击。P猜未公开nonce的空间不因此改变。opaque retained/snapshot tags必须连同body/session/context使用，不能单凭随机tag相等推出output相同或默认为全球唯一。

## 8. 执行时间/存储模型的负边界

Prio rejection loop确实可变，但真RO候选流的拒绝计数K与最终canonical field值Y精确独立，联合概率 `ρ^k/2^128=Pr[K=k]/q`；同seed/offset需保留同原始候选流。若为每次exact retry重新抽K，相关trace分布错误；若把所有拒绝事件丢为可忽略，预算也可能不正确。真实count不是额外metadata，必须在同native混合中构造。

旧secret-bit scalar/inverse、decide前缀早退、TOAST压缩、secret hex/JSON或status整载荷decode都不能直接叫“OS噪声”。这些发现与实际003修复已在冻结G4a08保留。本轮适用的是标准fixed-primitive instruction/address/IO模型、具体debug不变量、9列EXTERNAL+WALoff/无传输压缩、raw固定BYTEA/EXISTS。它不自动推广到任意ISA、编译器、power/EM、共驻窥探或值相关硬件时长。

client opening decimal parser/prover只在可信input-ready之前本地执行；线上mask/rho为16/32B，sidecar plaintext93B。若实际部署计算完即发送而暴露client生成时间，不能把它追加进公开metadata宣称本证明覆盖；即时发送的功能harness不提供client timing安全证据。

## 9. 可复现负控制、G5与状态含义

执行 `python3 -B sources/refinement/check_refinement.py --output-directory sources/refinement/check-005`（以本目录为cwd）。输出固定脚本SHA和52个source ranges；冻结build003全部288源码匹配。Python正图840状态/2652边穷尽，8个mutant分别违反lock-before-prepare、complete-snapshot、persist-before-send（未bind和crash丢snapshot两个）、unique-protected-branch、exactly-once-apply、exposure-monotone、abort-preserves-prefix，均保留完整最短event/state trace。check001–004的输出和旧脚本保留，不将新语义说明追写旧结果。

这些是预先指定删除守卫的敏感性控制，出现反例是控制成功，不是新源漏洞。数学histogram/K/moment/context/weakSE检查只验证具体等式，不能测试密码学安全或以有限遍历替代05的任意prefix证明。正图模型不含完整真实history、proof、实际数据库或网络，未声称自动建立实现精化。

G5 E5/1及其35例是独立有限旁证：变量需按05翻译，flag/captured-slot抽象必须说明；没有直接导入其PASS作为新g4a-source无界证明，也未执行G5 native crash/race或故障扩展。旧G3历史结果仅按原source/run生效。本轮G4b结论以其最终精确document/source/artifact清单及独立review为准，不通过更名或删反例追认旧证据。
