/* 语法·命令·计算 专项练习（drills）
   结构：window.DRILLS[单元id] = {topic, items:[...]}
   题型 type: choice单选 multi多选 judge判断 fill填空 blanks多空填空 cmd命令书写 fix改错 pair配对 group归类 order排序 calc计算
   每题必须带 source（来源标注，不得虚构）。
   覆盖矩阵见 资料/drills_coverage.md */
window.DRILLS = {
  "G2-3.1": {
    topic: "iptables 防火墙规则与命令",
    items: [
      { id:"DL-ipt-01", type:"choice", q:"iptables 默认操作的表是哪个？", options:[{key:"A",text:"nat"},{key:"B",text:"mangle"},{key:"C",text:"filter"},{key:"D",text:"raw"}], answer:"C", answerView:"filter", analysis:"不指定 -t 时默认使用 filter 表（数据包过滤）。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-02", type:"multi", q:"filter 表中内置的三条链是？", options:[{key:"A",text:"INPUT"},{key:"B",text:"FORWARD"},{key:"C",text:"OUTPUT"},{key:"D",text:"PREROUTING"}], answer:["A","B","C"], answerView:"INPUT / FORWARD / OUTPUT", analysis:"filter 表只处理本机与转发数据，含 INPUT、FORWARD、OUTPUT；PREROUTING/POSTROUTING 属 nat/mangle。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-03", type:"choice", q:"nat 表中最常见的两条链是？", options:[{key:"A",text:"INPUT、OUTPUT"},{key:"B",text:"PREROUTING、POSTROUTING"},{key:"C",text:"FORWARD、INPUT"},{key:"D",text:"PREROUTING、INPUT"}], answer:"B", answerView:"PREROUTING、POSTROUTING", analysis:"nat 表在路由前(PREROUTING)做目的地址转换、路由后(POSTROUTING)做源地址转换。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-04", type:"judge", q:"iptables -A 表示在链尾追加一条规则，-I 表示插入到链首（或指定位置）。", answer:"T", answerView:"正确", analysis:"-A 追加；-I 可带序号插入，不带序号默认插到第 1 条。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-05", type:"judge", q:"iptables -P INPUT ACCEPT 的作用是把 INPUT 链的默认策略设为 ACCEPT。", answer:"T", answerView:"正确", analysis:"-P 用于设置链的默认策略（ACCEPT/DROP）。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-06", type:"fill", q:"补全命令：允许外部访问本机 22 端口（TCP）——\niptables -A INPUT -p tcp ＿＿＿ 22 -j ACCEPT", answer:"--dport", alts:["--dport","--dport="], answerView:"--dport", analysis:"--dport 指定目的端口（--sport 为源端口）。", source:"来源：2022下半年案例试题一 问题5（iptables 配置）" },
      { id:"DL-ipt-07", type:"fill", q:"补全命令：拒绝来自 192.168.1.100 的所有入站流量——\niptables -A INPUT ＿＿＿ 192.168.1.100 -j DROP", answer:"-s", alts:["-s","--source","-s="], answerView:"-s", analysis:"-s 指定源地址（--source 同义）。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-08", type:"choice", q:"下列哪种动作会丢弃数据包并**不回**任何信息？", options:[{key:"A",text:"ACCEPT"},{key:"B",text:"DROP"},{key:"C",text:"REJECT"},{key:"D",text:"LOG"}], answer:"B", answerView:"DROP", analysis:"DROP 静默丢弃；REJECT 会回 ICMP 不可达/TCP RST；LOG 只记录不处理。", source:"来源：2019上半年案例试题四 问题3（三种数据包处理方式）" },
      { id:"DL-ipt-09", type:"multi", q:"防火墙对数据包常见的处理方式包括？", options:[{key:"A",text:"接受 Accept"},{key:"B",text:"丢弃 Drop"},{key:"C",text:"拒绝 Reject"},{key:"D",text:"加密 Encrypt"}], answer:["A","B","C"], answerView:"接受 / 丢弃 / 拒绝", analysis:"三种处理方式：接受、丢弃、拒绝；加密不属于数据包处理方式。", source:"来源：2019上半年案例试题四 问题3" },
      { id:"DL-ipt-10", type:"judge", q:"iptables 规则表自上而下匹配，一旦匹配成功就执行对应动作，不再继续向下匹配。", answer:"T", answerView:"正确", analysis:"规则顺序敏感，命中即执行；因此精确规则应放在宽泛规则之前。", source:"来源：2019上半年案例试题四 问题2（缺省/规则顺序）" },
      { id:"DL-ipt-11", type:"cmd", q:"写出命令：允许本机主动发起的连接返回的数据包（已建立或相关连接）进入。", answerView:"iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT", analysis:"用 -m state --state ESTABLISHED,RELATED 放行已建立/相关连接；也可用 -m conntrack --ctstate。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-12", type:"cmd", q:"场景：要求把 INPUT 链默认策略设为“丢弃”，并放行本机 80 端口（TCP）入站。写出两条命令。", answerView:"iptables -P INPUT DROP\niptables -A INPUT -p tcp --dport 80 -j ACCEPT", analysis:"先设默认策略为 DROP，再逐条放行必要服务（白名单思路）。", source:"来源：2022下半年案例试题一 问题5" },
      { id:"DL-ipt-13", type:"cmd", q:"写出命令：禁止 192.168.1.0/24 网段访问本机 3389 端口。", answerView:"iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 3389 -j DROP", analysis:"用网段 + -p tcp + --dport 指定目的端口。", source:"来源：2022下半年案例试题三 问题4（用防火墙隔离被控主机）" },
      { id:"DL-ipt-14", type:"fix", q:"下面命令有误，请改正：\niptables -A INPUT --p tcp --dport 22 -j ACCEPT", answerView:"iptables -A INPUT -p tcp --dport 22 -j ACCEPT", analysis:"指定协议用 -p（不是 --p）。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-15", type:"fix", q:"下面命令有误，请改正：\niptables -P INPUT -j DROP", answerView:"iptables -P INPUT DROP", analysis:"-P 直接跟策略名（ACCEPT/DROP），不加 -j。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-16", type:"choice", q:"查看现有规则并显示行号，正确的命令是？", options:[{key:"A",text:"iptables -L -n"},{key:"B",text:"iptables -L -n --line-numbers"},{key:"C",text:"iptables -F -n"},{key:"D",text:"iptables -S -v"}], answer:"B", answerView:"iptables -L -n --line-numbers", analysis:"-L 列出、-n 不做域名解析、--line-numbers 显示行号（便于 -D 删除）。", source:"来源：2022下半年案例试题一 问题3（查看规则）" },
      { id:"DL-ipt-17", type:"choice", q:"删除 INPUT 链中第 3 条规则的命令是？", options:[{key:"A",text:"iptables -D INPUT 3"},{key:"B",text:"iptables -R INPUT 3"},{key:"C",text:"iptables -F INPUT 3"},{key:"D",text:"iptables -X INPUT 3"}], answer:"A", answerView:"iptables -D INPUT 3", analysis:"-D 删除（可跟规则内容或行号）；-F 清空、-X 删除自定义链。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-18", type:"judge", q:"iptables -F 会清空指定链（或全部链）中的所有规则，但不会改变链的默认策略。", answer:"T", answerView:"正确", analysis:"-F 只清规则；默认策略需用 -P 修改。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-19", type:"choice", q:"要让内网主机共享上网（S-NAT），应在 nat 表的哪条链做源地址转换？", options:[{key:"A",text:"PREROUTING"},{key:"B",text:"POSTROUTING"},{key:"C",text:"INPUT"},{key:"D",text:"FORWARD"}], answer:"B", answerView:"POSTROUTING", analysis:"SNAT/MASQUERADE 在 POSTROUTING；DNAT 在 PREROUTING。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-20", type:"fill", q:"补全命令：把本机 80 端口流量重定向到 8080（nat 表）——\niptables -t nat -A PREROUTING -p tcp --dport 80 -j ＿＿＿ --to-port 8080", answer:"REDIRECT", alts:["REDIRECT"], answerView:"REDIRECT", analysis:"REDIRECT 用于本机端口重定向；跨主机需用 DNAT --to-destination。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-21", type:"order", q:"请按数据包进入本机的处理顺序排列（↑↓ 调整）：", steps:["数据包到达网卡","PREROUTING 链（nat/mangle）","路由决策：发往本机或转发","INPUT 链（filter）","交给本机上层应用"], shuffled:["路由决策：发往本机或转发","数据包到达网卡","交给本机上层应用","INPUT 链（filter）","PREROUTING 链（nat/mangle）"], answerView:"网卡 → PREROUTING → 路由决策 → INPUT → 上层应用", analysis:"入站路径：网卡→PREROUTING→路由→INPUT→应用；转发的包走 FORWARD。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-22", type:"pair", q:"匹配 iptables 参数与含义：", left:[{k:"-A"},{k:"-I"},{k:"-P"},{k:"-F"},{k:"-j"}], right:["追加规则到链尾","插入规则到链首/指定位置","设置链默认策略","清空链中所有规则","指定匹配后执行的动作"], answer:["0","1","2","3","4"], answerView:"-A追加 / -I插入 / -P默认策略 / -F清空 / -j动作", analysis:"记住五个高频参数即可读写多数规则。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-23", type:"group", q:"把下列命令归入对应操作类别：", left:[{k:"iptables -L -n --line-numbers"},{k:"iptables -D INPUT 3"},{k:"iptables -P INPUT DROP"},{k:"iptables-save > rules.bak"}], groups:["查看","删除","策略","保存"], answer:["查看","删除","策略","保存"], answerView:"查看/删除/策略/保存", analysis:"-L 查看；-D 删除；-P 策略；iptables-save 保存、iptables-restore 恢复。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-24", type:"judge", q:"在 Ubuntu 上，iptables 规则默认重启后会丢失，需要持久化保存（如 iptables-persistent/netfilter-persistent）。", answer:"T", answerView:"正确", analysis:"案例中常考“规则持久化”：保存到 /etc/iptables/rules.v4 等。", source:"来源：2022下半年案例试题一 问题5（Ubuntu 自带 iptables）" },
      { id:"DL-ipt-25", type:"choice", q:"默认策略为 DROP 时，下列哪条规则最应放在前面？", options:[{key:"A",text:"放行已建立连接的 ESTABLISHED,RELATED"},{key:"B",text:"放行任意来源任意端口"},{key:"C",text:"拒绝所有 ICMP"},{key:"D",text:"记录所有日志"}], answer:"A", answerView:"放行 ESTABLISHED,RELATED", analysis:"先放行已建立/相关连接，再放行必要服务，否则回包会被默认策略丢弃。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-26", type:"fill", q:"补全：只允许 eth0 网卡进入的 SSH 流量——\niptables -A INPUT ＿＿＿ eth0 -p tcp --dport 22 -j ACCEPT", answer:"-i", alts:["-i"], answerView:"-i", analysis:"-i 指定入接口；出接口用 -o。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-27", type:"judge", q:"REJECT 与 DROP 的区别在于：REJECT 会给发送方返回错误信息，而 DROP 不会。", answer:"T", answerView:"正确", analysis:"内网可用 REJECT（便于排障），对外网边界常用 DROP（不暴露信息）。", source:"来源：2019上半年案例试题四 问题3" },
      { id:"DL-ipt-28", type:"cmd", q:"写出命令：记录（LOG）所有发往 23 端口的入站数据包，前缀标注 TELNET（不阻断）。", answerView:"iptables -A INPUT -p tcp --dport 23 -j LOG --log-prefix \"TELNET \"", analysis:"LOG 为“非终结”目标，记录后继续匹配后续规则。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-29", type:"blanks", q:"某主机只需对外开放 80、443、22（TCP），其余全拒绝。请补全两条命令：", blanks:[{label:"设置默认策略", answer:"iptables -P INPUT DROP", alts:["iptables -P INPUT DROP"]},{label:"放行 Web(80/443)", answer:"iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT", alts:["iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT","iptables -A INPUT -p tcp --dport 80 -j ACCEPT;iptables -A INPUT -p tcp --dport 443 -j ACCEPT"]}], answerView:"iptables -P INPUT DROP；iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT", analysis:"用 -m multiport --dports 可一次匹配多个端口。", source:"来源：iptables 命令语法（自编练习）" },
      { id:"DL-ipt-30", type:"choice", q:"规则链的“默认策略”通常用哪种动作组合？", options:[{key:"A",text:"ACCEPT / DROP"},{key:"B",text:"LOG / REJECT"},{key:"C",text:"SNAT / DNAT"},{key:"D",text:"RETURN / QUEUE"}], answer:"A", answerView:"ACCEPT / DROP", analysis:"默认策略只允许 ACCEPT 或 DROP。", source:"来源：iptables 命令语法（自编练习）" }
    ]
  },
  "G2-3.2": {
    topic: "Wireshark 显示过滤 / Snort 规则语法",
    items: [
      { id:"DL-ws-01", type:"choice", q:"Wireshark 中“显示过滤器”的作用是？", options:[{key:"A",text:"在抓包时丢弃不需要的包"},{key:"B",text:"在已抓到的数据包中筛选显示"},{key:"C",text:"修改数据包内容"},{key:"D",text:"重新发送数据包"}], answer:"B", answerView:"在已抓到的包中筛选显示", analysis:"显示过滤器只影响显示；抓包过滤器(capture filter)在捕获阶段生效、语法不同。", source:"来源：2022下半年案例试题三 问题3（显示过滤表达式）" },
      { id:"DL-ws-02", type:"fill", q:"补全显示过滤表达式：只显示与 192.168.1.100 相关的所有流量。\n过滤框输入：＿＿＿ == 192.168.1.100", answer:"ip.addr", alts:["ip.addr","ip.addr=="], answerView:"ip.addr == 192.168.1.100", analysis:"ip.addr 同时匹配源或目的地址；只匹配源用 ip.src、目的用 ip.dst。", source:"来源：2022下半年案例试题三 问题3" },
      { id:"DL-ws-03", type:"fill", q:"补全显示过滤表达式：只显示 TCP 目的端口为 3389 的流量。\n过滤框输入：tcp.＿＿＿ == 3389", answer:"dstport", alts:["dstport"], answerView:"tcp.dstport == 3389", analysis:"tcp.dstport 目的端口；tcp.srcport 源端口；tcp.port 匹配源或目的。", source:"来源：2023下半年案例试题四 问题4（过滤表达式）" },
      { id:"DL-ws-04", type:"cmd", q:"写出显示过滤表达式：筛查“源地址 192.168.69.69 且目的地址 192.168.1.100”的流量。", answerView:"ip.src == 192.168.69.69 && ip.dst == 192.168.1.100", analysis:"用 &&（或 and）连接两个条件；也可写 ip.addr==a && ip.addr==b。", source:"来源：2023下半年案例试题四 问题4" },
      { id:"DL-ws-05", type:"judge", q:"Wireshark 显示过滤器中，“==”比较、“&&/and”与、“||/or”或、“!=”不等、“!”非均可用于组合条件。", answer:"T", answerView:"正确", analysis:"显示过滤支持英文与符号两种写法，如 tcp.port==80 && http。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-06", type:"choice", q:"只想看 HTTP 的 GET 请求，过滤表达式应为？", options:[{key:"A",text:"http == GET"},{key:"B",text:"http.request.method == \"GET\""},{key:"C",text:"tcp.port == 80 && GET"},{key:"D",text:"http.get"}], answer:"B", answerView:"http.request.method == \"GET\"", analysis:"HTTP 字段形如 http.request.method、http.host、http.response.code。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-07", type:"choice", q:"过滤 SYN 包（TCP 标志位 SYN=1）应使用？", options:[{key:"A",text:"tcp.syn"},{key:"B",text:"tcp.flags.syn == 1"},{key:"C",text:"tcp.flags == 1"},{key:"D",text:"tcp.flag.syn"}], answer:"B", answerView:"tcp.flags.syn == 1", analysis:"TCP 标志位形如 tcp.flags.syn/ack/fin/rst；也可 tcp.flags & 0x02。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-08", type:"fill", q:"补全过滤：只显示 DNS 协议报文。\n过滤框输入：＿＿＿", answer:"dns", alts:["dns","udp.port==53","udp.port == 53"], answerView:"dns（或 udp.port == 53）", analysis:"直接写协议名可过滤该协议；也可按端口 udp.port==53。", source:"来源：2021下半年案例试题三（DNS 隐蔽通道分析）" },
      { id:"DL-ws-09", type:"judge", q:"显示过滤支持 contains 运算符，用于在字段中查找字符串，如 http.host contains \"baidu\"。", answer:"T", answerView:"正确", analysis:"contains 做子串匹配；~ 或 matches 用于正则匹配。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-10", type:"pair", q:"匹配 Wireshark 过滤字段与含义：", left:[{k:"ip.src"},{k:"ip.dst"},{k:"tcp.port"},{k:"http.host"},{k:"frame.len"}], right:["源 IP 地址","目的 IP 地址","TCP 源或目的端口","HTTP 请求的 Host 字段","帧长度"], answer:["0","1","2","3","4"], answerView:"ip.src/ip.dst/tcp.port/http.host/frame.len", analysis:"常用字段名需记牢，写表达式时直接引用。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-11", type:"cmd", q:"写出过滤表达式：找出长度小于 100 字节的 ICMP 数据包。", answerView:"icmp && frame.len < 100", analysis:"协议名 + frame.len 比较；支持 < > <= >=。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-12", type:"choice", q:"只想查看第 100～200 号数据包，应使用？", options:[{key:"A",text:"frame.number >= 100 && frame.number <= 200"},{key:"B",text:"frame >= 100"},{key:"C",text:"no == 100-200"},{key:"D",text:"number(100,200)"}], answer:"A", answerView:"frame.number >= 100 && frame.number <= 200", analysis:"帧序号字段为 frame.number。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-13", type:"group", q:"把下列表达式归入“显示过滤 / 抓包过滤”：", left:[{k:"tcp.port == 80"},{k:"host 192.168.1.1"},{k:"http.request.method == \"POST\""},{k:"port 3389"}], groups:["显示过滤器","抓包过滤器"], answer:["显示过滤器","抓包过滤器","显示过滤器","抓包过滤器"], answerView:"tcp.port==80/http.* 是显示过滤；host/port 是抓包过滤(BPF)", analysis:"抓包过滤用 BPF 语法(host/port/net)，显示过滤用字段名(协议.字段)。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-14", type:"fix", q:"下面表达式有误，请改正（应为逻辑“与”）：\nip.addr == 1.1.1.1 & ip.addr == 2.2.2.2", answerView:"ip.addr == 1.1.1.1 && ip.addr == 2.2.2.2", analysis:"单个 & 是位运算，逻辑与必须写 &&（或 and）。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-15", type:"blanks", q:"补全两个表达式（各一空）：", blanks:[{label:"只看 80 端口 HTTP", answer:"tcp.port == 80", alts:["tcp.port==80","tcp.port == 80"]},{label:"只看 ICMP", answer:"icmp", alts:["icmp"]}], answerView:"tcp.port == 80；icmp", analysis:"按端口过滤用 xxx.port，按协议直接写协议名。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-16", type:"judge", q:"Wireshark 显示过滤表达式区分大小写（如 ip.addr 与 IP.ADDR 不等价）。", answer:"T", answerView:"正确", analysis:"字段名区分大小写；协议名通常小写。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-ws-17", type:"choice", q:"要把抓到的包导出为可再次打开的格式，应使用？", options:[{key:"A",text:"File → Export Specified Packets（.pcapng）"},{key:"B",text:"File → Print"},{key:"C",text:"Statistics → Summary"},{key:"D",text:"Analyze → Follow TCP Stream"}], answer:"A", answerView:"File → Export Specified Packets(.pcapng)", analysis:"导出为 .pcap/.pcapng 便于归档与复查；Follow TCP Stream 用于还原会话内容。", source:"来源：Wireshark 显示过滤语法（自编练习）" },
      { id:"DL-snort-01", type:"choice", q:"Snort 规则中，规则头由哪几部分组成？", options:[{key:"A",text:"动作 协议 源地址/端口 方向 目的地址/端口"},{key:"B",text:"动作 规则选项 告警 记录"},{key:"C",text:"协议 端口 sid rev"},{key:"D",text:"alert tcp sid msg"}], answer:"A", answerView:"动作 协议 源 方向 目的", analysis:"规则头=动作+协议+源IP/端口+方向(->或<>)+目的IP/端口；其后的括号内为规则选项。", source:"来源：2021下半年案例试题一 问题5（Snort 规则）" },
      { id:"DL-snort-02", type:"fill", q:"补全 Snort 规则中的“告警”动作：\n＿＿＿ tcp any any -> any any (msg:\"XXX\"; sid:1106;)", answer:"alert", alts:["alert"], answerView:"alert（告警）", analysis:"常见动作：alert(告警)、log(记录)、pass(放行)、drop(丢弃/需inline)。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-03", type:"judge", q:"Snort 规则中转义符“->”表示单向流量，源在前、目的在后；“<>”表示双向。", answer:"T", answerView:"正确", analysis:"方向操作符：-> 单向，<> 双向。", source:"来源：Snort 规则语法（自编练习）" },
      { id:"DL-snort-04", type:"multi", q:"下列属于 Snort 规则**选项**（括号内）的有？", options:[{key:"A",text:"msg"},{key:"B",text:"content"},{key:"C",text:"sid"},{key:"D",text:"tcp"}], answer:["A","B","C"], answerView:"msg / content / sid（tcp 属规则头）", analysis:"括号内为选项：msg 描述、content 匹配内容、sid 规则号、rev 版本、classtype 分类等。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-05", type:"choice", q:"Snort 规则中用来匹配报文内容（如 union select）的选项是？", options:[{key:"A",text:"msg"},{key:"B",text:"content"},{key:"C",text:"sid"},{key:"D",text:"nocase"}], answer:"B", answerView:"content", analysis:"content 指定要匹配的字节串；nocase 表示忽略大小写。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-06", type:"judge", q:"Snort 的 sid 是规则唯一编号，自定义规则一般使用 1000000 以上的编号。", answer:"T", answerView:"正确", analysis:"sid=规则标识；rev 表示规则修订号。", source:"来源：Snort 规则语法（自编练习）" },
      { id:"DL-snort-07", type:"fill", q:"补全：忽略 content 匹配的大小写，应使用选项 ＿＿＿。\nmsg:\"XXX\"; content:\"union\"; ＿＿＿; sid:1106;", answer:"nocase", alts:["nocase"], answerView:"nocase", analysis:"nocase 使 content 匹配不区分大小写。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-08", type:"cmd", q:"写出 Snort 规则：对任意 TCP 流量中出现字符串 \"union select\" 的报文告警，忽略大小写，规则号 1000101。", answerView:"alert tcp any any -> any any (msg:\"SQL Injection\"; content:\"union select\"; nocase; sid:1000101;)", analysis:"规则头 + 选项（msg/content/nocase/sid）；末尾用分号结束。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-09", type:"order", q:"按 Snort 规则书写顺序排列（↑↓ 调整）：", steps:["动作(alert)","协议(tcp)","源地址/端口(any any)","方向(->)","目的地址/端口(any any)","规则选项(...)"], shuffled:["协议(tcp)","动作(alert)","规则选项(...)","方向(->)","源地址/端口(any any)","目的地址/端口(any any)"], answerView:"alert tcp any any -> any any (选项)", analysis:"先规则头（动作 协议 源 方向 目的），再括号内选项。", source:"来源：2021下半年案例试题一 问题5" },
      { id:"DL-snort-10", type:"pair", q:"匹配 Snort 选项与含义：", left:[{k:"msg"},{k:"content"},{k:"sid"},{k:"rev"},{k:"classtype"}], right:["告警/记录时的提示信息","匹配的报文内容","规则唯一编号","规则修订版本号","规则分类"], answer:["0","1","2","3","4"], answerView:"msg/content/sid/rev/classtype", analysis:"高频五选项；写规则时至少要 msg + sid。", source:"来源：Snort 规则语法（自编练习）" },
      { id:"DL-snort-11", type:"group", q:"把下列 Snort 要素归入“规则头 / 规则选项”：", left:[{k:"alert"},{k:"content"},{k:"tcp"},{k:"sid"},{k:"->"}], groups:["规则头","规则选项"], answer:["规则头","规则选项","规则头","规则选项","规则头"], answerView:"alert/tcp/-> 属规则头；content/sid 属选项", analysis:"规则头描述“谁对谁、什么协议、什么动作”；选项描述“匹配什么、怎么告警”。", source:"来源：Snort 规则语法（自编练习）" },
      { id:"DL-snort-12", type:"judge", q:"IDS 通常是“旁路”部署（只检测不阻断），IPS 是“串联”部署（可实时阻断）。", answer:"T", answerView:"正确", analysis:"IDS 被动检测、IPS 在线阻断；案例中常考两者区别。", source:"来源：2018上半年案例试题五（IDS/IPS 与 Snort）" }
    ]
  },
  "G2-4.1": {
    topic: "Windows 日志与事件ID / Linux 日志与命令 / Linux 权限换算",
    items: [
      { id:"DL-win-01", type:"choice", q:"Windows 安全日志中，事件 ID 4624 表示？", options:[{key:"A",text:"登录失败"},{key:"B",text:"登录成功"},{key:"C",text:"注销"},{key:"D",text:"账号锁定"}], answer:"B", answerView:"登录成功", analysis:"4624 登录成功、4625 登录失败，是案例中最常考的一对。", source:"来源：2023下半年案例试题四 问题2（事件ID 4625）" },
      { id:"DL-win-02", type:"choice", q:"事件 ID 4625 表示？", options:[{key:"A",text:"成功登录"},{key:"B",text:"失败登录"},{key:"C",text:"创建用户"},{key:"D",text:"清除日志"}], answer:"B", answerView:"登录失败", analysis:"大量 4625 是暴力破解的典型特征。", source:"来源：2023下半年案例试题四 问题2" },
      { id:"DL-win-03", type:"pair", q:"匹配 Windows 事件 ID 与含义：", left:[{k:"4624"},{k:"4625"},{k:"4634"},{k:"4672"},{k:"4720"}], right:["登录成功","登录失败","注销","授予特殊权限","创建用户"], answer:["0","1","2","3","4"], answerView:"4624登录成功/4625登录失败/4634注销/4672特殊权限/4720创建用户", analysis:"登录类：4624/4625/4634/4647/4648/4672；账户类：4720/4722/4724/4725/4726/4740。", source:"来源：教材19.2 Windows 操作系统安全分析与防护" },
      { id:"DL-win-04", type:"fill", q:"补全：Windows 日志文件的扩展名是 ＿＿＿（Vista 及以后）。", answer:".evtx", alts:[".evtx","evtx"], answerView:".evtx（XP 为 .evt）", analysis:"事件日志文件默认位于 C:\\Windows\\System32\\winevt\\Logs。", source:"来源：2022下半年案例试题三 问题2（日志文件格式）" },
      { id:"DL-win-05", type:"fill", q:"补全：通过命令行窗口打开“事件查看器”的命令是 ＿＿＿。", answer:"eventvwr", alts:["eventvwr","eventvwr.msc"], answerView:"eventvwr（或 eventvwr.msc）", analysis:"开始→运行输入 eventvwr.msc 也可打开。", source:"来源：2023下半年案例试题四 问题1" },
      { id:"DL-win-06", type:"choice", q:"Windows 系统日志分为三大类，下列不属于的是？", options:[{key:"A",text:"系统日志"},{key:"B",text:"应用程序日志"},{key:"C",text:"安全日志"},{key:"D",text:"网络日志"}], answer:"D", answerView:"系统 / 应用程序 / 安全（无“网络日志”）", analysis:"三类日志：系统、应用程序、安全；安全日志记录登录/审核事件。", source:"来源：2019上半年案例试题四（缺省规则以外的日志分类）" },
      { id:"DL-win-07", type:"cmd", q:"写出命令：用命令行工具导出“安全”日志到文件。", answerView:"wevtutil epl Security C:\\sec.evtx", analysis:"wevtutil epl 日志名 目标文件；wevtutil qe 可查询、wevtutil cl 清除。", source:"来源：Windows 事件日志命令（自编练习）" },
      { id:"DL-win-08", type:"judge", q:"Windows 安全日志默认只有管理员（Administrators）有权查看。", answer:"T", answerView:"正确", analysis:"安全日志的访问受 ACL 限制，普通用户无法查看。", source:"来源：教材19.2 Windows 操作系统安全分析与防护" },
      { id:"DL-win-09", type:"choice", q:"事件 ID 1102 表示？", options:[{key:"A",text:"审核日志被清除"},{key:"B",text:"系统启动"},{key:"C",text:"用户登录"},{key:"D",text:"服务启动"}], answer:"A", answerView:"审核日志被清除", analysis:"1102 常是攻击者清理痕迹的信号，排查时要重点关注。", source:"来源：Windows 事件日志（自编练习）" },
      { id:"DL-win-10", type:"group", q:"把下列事件 ID 归入对应类别：", left:[{k:"4625"},{k:"4726"},{k:"4672"},{k:"4740"}], groups:["登录认证类","账户管理类"], answer:["登录认证类","账户管理类","登录认证类","账户管理类"], answerView:"4625/4672 属登录认证；4726/4740 属账户管理", analysis:"4740 账户锁定既与认证相关，此处归账户管理类（锁定状态变化）。", source:"来源：Windows 事件日志（自编练习）" },
      { id:"DL-win-11", type:"fill", q:"补全：登录类型 3 表示 ＿＿＿ 登录（如访问共享、远程桌面之外的网络认证）。", answer:"网络", alts:["网络","network"], answerView:"网络登录（Type 3）", analysis:"常见登录类型：2 交互、3 网络、10 远程交互(RDP)。", source:"来源：Windows 安全日志登录类型（自编练习）" },
      { id:"DL-win-12", type:"judge", q:"短时间内出现大量 4625 且来源 IP 集中，通常可判断为暴力破解攻击。", answer:"T", answerView:"正确", analysis:"案例中常据此判断 RDP/共享口令爆破。", source:"来源：2022下半年案例试题三（RDP 暴力破解）" },
      { id:"DL-win-13", type:"fill", q:"补全：远程桌面协议（RDP）默认使用 TCP 端口 ＿＿＿。", answer:"3389", alts:["3389"], answerView:"3389", analysis:"RDP 默认 3389，是暴力破解的高发端口。", source:"来源：2022下半年案例试题三 问题5（端口判断）" },
      { id:"DL-win-14", type:"choice", q:"要查看“审核日志是否被清除”，应重点筛选哪个事件 ID？", options:[{key:"A",text:"4624"},{key:"B",text:"1102"},{key:"C",text:"4720"},{key:"D",text:"6005"}], answer:"B", answerView:"1102", analysis:"1102=日志被清除；6005/6006=事件日志服务启动/停止。", source:"来源：Windows 事件日志（自编练习）" },
      { id:"DL-win-15", type:"blanks", q:"某主机被爆破，请在日志中筛选并统计失败登录次数（各一空）：", blanks:[{label:"筛选命令(事件ID)", answer:"4625", alts:["4625"]},{label:"列含义(事件ID44625)", answer:"登录失败", alts:["登录失败"]}], answerView:"筛选 4625；4625=登录失败", analysis:"事件查看器“筛选当前日志”→按事件 ID 4625 筛选。", source:"来源：2023下半年案例试题四 问题2" },
      { id:"DL-win-16", type:"pair", q:"匹配登录类型与含义：", left:[{k:"Type 2"},{k:"Type 3"},{k:"Type 10"},{k:"Type 5"}], right:["交互式登录（本地控制台）","网络登录（访问共享等）","远程交互（RDP）","服务启动登录"], answer:["0","1","2","3"], answerView:"2交互/3网络/10远程交互/5服务", analysis:"判断“本地成功登录 vs 网络登录”时必看登录类型。", source:"来源：2023下半年案例试题四 问题2（备选项判断）" },
      { id:"DL-win-17", type:"order", q:"请按应急排查思路排列（↑↓ 调整）：", steps:["查看安全日志失败登录(4625)","确定来源IP与账号","检查是否被成功登录(4624)","检查账号是否被新建/提权(4720/4672)","检查日志是否被清除(1102)"], shuffled:["确定来源IP与账号","查看安全日志失败登录(4625)","检查日志是否被清除(1102)","检查是否被成功登录(4624)","检查账号是否被新建/提权(4720/4672)"], answerView:"查询→定位→确认入侵→检查权限变更→确认痕迹清除", analysis:"先找失败线索，再确认是否突破，最后查提权与清痕。", source:"来源：2022下半年案例试题三 / 2023下半年案例试题四" },
      { id:"DL-win-18", type:"fix", q:"下面命令有误，请改正（查看安全日志最近 10 条）：\nwevtutil qe Security /c:10 /rd:true /f:text /n", answerView:"wevtutil qe Security /c:10 /rd:true /f:text", analysis:"/n 用于按事件ID筛选且需带值(如 /q)，此处多余。", source:"来源：Windows 事件日志命令（自编练习）" },
      { id:"DL-win-19", type:"choice", q:"Windows 系统事件 ID 6005 表示？", options:[{key:"A",text:"事件日志服务已启动"},{key:"B",text:"系统关机"},{key:"C",text:"服务安装失败"},{key:"D",text:"用户注销"}], answer:"A", answerView:"事件日志服务已启动（≈系统开机）", analysis:"6005/6006 可用于判断开机与关机时间。", source:"来源：Windows 事件日志（自编练习）" },
      { id:"DL-win-20", type:"cmd", q:"写出命令：列出“应用程序”日志中最近 20 条记录（wevtutil）。", answerView:"wevtutil qe Application /c:20 /rd:true /f:text", analysis:"qe 查询、/c 条数、/rd 逆序(最新在前)、/f 输出格式。", source:"来源：Windows 事件日志命令（自编练习）" },
      { id:"DL-win-21", type:"judge", q:"Windows 日志文件可以用记事本直接打开 .evtx 并正常阅读。", answer:"F", answerView:"错误（.evtx 为二进制，需事件查看器/wevtutil）", analysis:".evtx 是二进制格式，需用事件查看器或解析工具打开。", source:"来源：Windows 事件日志（自编练习）" },
      { id:"DL-win-22", type:"choice", q:"判断“本地成功登录”还是“网络失败登录”，除事件 ID 外还必须结合？", options:[{key:"A",text:"任务类别/登录类型/进程名"},{key:"B",text:"文件大小"},{key:"C",text:"磁盘型号"},{key:"D",text:"网卡 MAC"}], answer:"A", answerView:"任务类别/登录类型等字段", analysis:"案例题干明确要求“结合任务类别”判断。", source:"来源：2023下半年案例试题四 问题2" },
      { id:"DL-win-23", type:"fill", q:"补全：读取登录失败记录的命令行工具是 ＿＿＿（lastb 的 Windows 类比可用事件查看器筛选）。\n（此题填 Linux 端命令）", answer:"lastb", alts:["lastb"], answerView:"lastb（Linux 查看失败登录）", analysis:"Linux: lastb 读 /var/log/btmp、last 读 /var/log/wtmp。", source:"来源：Linux 日志文件与命令（自编练习）" },
      { id:"DL-win-24", type:"multi", q:"下列哪些属于 Windows 安全日志中与“账户管理”相关的事件 ID？", options:[{key:"A",text:"4720 创建用户"},{key:"B",text:"4726 删除用户"},{key:"C",text:"4724 重置口令"},{key:"D",text:"4624 登录成功"}], answer:["A","B","C"], answerView:"4720 / 4726 / 4724", analysis:"4624 属登录认证类。", source:"来源：Windows 事件日志（自编练习）" },

      { id:"DL-lnx-01", type:"choice", q:"RHEL/CentOS 下记录认证、登录相关信息的日志文件是？", options:[{key:"A",text:"/var/log/messages"},{key:"B",text:"/var/log/secure"},{key:"C",text:"/var/log/cron"},{key:"D",text:"/var/log/dmesg"}], answer:"B", answerView:"/var/log/secure", analysis:"Debian/Ubuntu 对应 /var/log/auth.log。", source:"来源：教材19.3.2 UNIX/Linux 安全机制（审计机制）" },
      { id:"DL-lnx-02", type:"fill", q:"补全：Linux 记录系统整体消息（内核、服务）的日志文件是 /var/log/＿＿＿。", answer:"messages", alts:["messages"], answerView:"/var/log/messages", analysis:"Debian 系列为 /var/log/syslog。", source:"来源：教材19.3.2 UNIX/Linux 安全机制" },
      { id:"DL-lnx-03", type:"pair", q:"匹配 Linux 日志文件与用途：", left:[{k:"/var/log/secure"},{k:"/var/log/messages"},{k:"/var/log/wtmp"},{k:"/var/log/btmp"},{k:"/var/log/cron"}], right:["认证/登录安全信息","系统与服务通用消息","成功登录历史(last)","失败登录记录(lastb)","定时任务执行日志"], answer:["0","1","2","3","4"], answerView:"secure认证/messages系统/wtmp成功登录/btmp失败登录/cron定时任务", analysis:"wtmp/btmp/lastlog 为二进制，用 last/lastb/lastlog 读取。", source:"来源：教材19.3.2 / 19.3.5" },
      { id:"DL-lnx-04", type:"fill", q:"补全：查看上一次登录信息（含每个用户最近登录时间）的命令是 ＿＿＿。", answer:"lastlog", alts:["lastlog"], answerView:"lastlog", analysis:"lastlog 读 /var/log/lastlog；last 读 wtmp；lastb 读 btmp。", source:"来源：Linux 日志与命令（自编练习）" },
      { id:"DL-lnx-05", type:"choice", q:"查看 systemd 管理的系统日志，应使用？", options:[{key:"A",text:"journalctl"},{key:"B",text:"messagectl"},{key:"C",text:"systat"},{key:"D",text:"logcat"}], answer:"A", answerView:"journalctl", analysis:"journalctl -u sshd 查看某服务日志；-n 50 查看最近 50 条。", source:"来源：教材19.3.5（最小化服务与日志审计）" },
      { id:"DL-lnx-06", type:"choice", q:"查看当前登录到系统的用户及来源 IP，应使用？", options:[{key:"A",text:"who / w"},{key:"B",text:"ls -l"},{key:"C",text:"df -h"},{key:"D",text:"free -m"}], answer:"A", answerView:"who / w", analysis:"w 比 who 多显示负载与活动；who -r 查看运行级别。", source:"来源：Linux 日志与命令（自编练习）" },
      { id:"DL-lnx-07", type:"cmd", q:"写出命令：查看本机所有 TCP 监听端口及对应进程（netstat）。", answerView:"netstat -tlnp", analysis:"-t TCP、-l 监听、-n 数字、-p 进程；ss -tlnp 为现代替代。", source:"来源：2021下半年案例试题一 问题3（netstat 查端口）" },
      { id:"DL-lnx-08", type:"choice", q:"下列哪个命令是 netstat 的现代替代品？", options:[{key:"A",text:"ss"},{key:"B",text:"ls"},{key:"C",text:"top"},{key:"D",text:"tar"}], answer:"A", answerView:"ss", analysis:"ss -tlnp 与 netstat -tlnp 等价且更快。", source:"来源：Linux 网络排查命令（自编练习）" },
      { id:"DL-lnx-09", type:"cmd", q:"写出命令：查看 3389 端口被哪个进程占用（lsof）。", answerView:"lsof -i:3389", analysis:"lsof -i :端口 查端口占用；也可 netstat -tlnp | grep 3389。", source:"来源：Linux 网络排查命令（自编练习）" },
      { id:"DL-lnx-10", type:"fill", q:"补全：查看密码（哈希）存放文件的路径是 /etc/＿＿＿。", answer:"shadow", alts:["shadow"], answerView:"/etc/shadow", analysis:"/etc/passwd 存账号信息（口令位为 x），/etc/shadow 存口令哈希。", source:"来源：2020下半年案例试题一（passwd/shadow）" },
      { id:"DL-lnx-11", type:"judge", q:"/etc/passwd 中每一行用冒号分隔为 7 个字段，第 3 个字段是 UID。", answer:"T", answerView:"正确", analysis:"字段：用户名:口令位:UID:GID:描述:主目录:登录shell。", source:"来源：2020下半年案例试题一 问题3" },
      { id:"DL-lnx-12", type:"fill", q:"补全：/etc/passwd 中，超级用户 root 的 UID 是 ＿＿＿。", answer:"0", alts:["0"], answerView:"0", analysis:"UID=0 即 root；1~499 系统用户；500/1000 起普通用户。", source:"来源：2020下半年案例试题一 问题3" },
      { id:"DL-lnx-13", type:"choice", q:"判断某账号是否允许登录（非 nologin），应查看 /etc/passwd 的哪一字段？", options:[{key:"A",text:"第 1 字段（用户名）"},{key:"B",text:"第 3 字段（UID）"},{key:"C",text:"第 6 字段（主目录）"},{key:"D",text:"第 7 字段（登录 shell）"}], answer:"D", answerView:"第 7 字段（登录 shell）", analysis:"shell 为 /sbin/nologin 或 /bin/false 表示不允许登录。", source:"来源：2020下半年案例试题一 问题4" },
      { id:"DL-lnx-14", type:"cmd", q:"写出命令：新建用户 testuser 并创建其主目录。", answerView:"useradd -m testuser", analysis:"-m 创建主目录；-s 指定 shell；-G 附加组。", source:"来源：2017上半年案例试题二（Windows 用户管理对照 Linux）" },
      { id:"DL-lnx-15", type:"cmd", q:"写出命令：修改用户 testuser 的口令。", answerView:"passwd testuser", analysis:"passwd 改自己口令；passwd 用户 由 root 改他人。", source:"来源：Linux 账号与口令管理（自编练习）" },
      { id:"DL-lnx-16", type:"fill", q:"补全：查看命令历史可执行 history 或读取文件 ~/.＿＿＿。", answer:"bash_history", alts:["bash_history"], answerView:"~/.bash_history", analysis:"应急排查时查看该文件可还原攻击者执行过的命令。", source:"来源：2021下半年案例试题三（攻击痕迹排查）" },
      { id:"DL-lnx-17", type:"cmd", q:"写出命令：查找系统中所有具有 SUID 权限的文件。", answerView:"find / -perm -4000 -type f", analysis:"SUID=4000；-type f 只看普通文件；2>/dev/null 可屏蔽报错。", source:"来源：2019上半年案例试题一 问题3（find -perm）" },
      { id:"DL-lnx-18", type:"fill", q:"补全：为文件 /tmp/a 创建符号链接 /tmp/b 的命令是 ln ＿＿＿ /tmp/a /tmp/b。", answer:"-s", alts:["-s"], answerView:"ln -s 目标 链接名", analysis:"软链接用 -s；硬链接不加参数。", source:"来源：2022下半年案例试题二（符号链接）" },
      { id:"DL-lnx-19", type:"choice", q:"在日志中检索包含 Failed 的行，应使用？", options:[{key:"A",text:"grep \"Failed\" /var/log/secure"},{key:"B",text:"cat /var/log/secure"},{key:"C",text:"ls /var/log"},{key:"D",text:"rm /var/log/secure"}], answer:"A", answerView:"grep \"Failed\" /var/log/secure", analysis:"grep 过滤关键词；配合 wc -l 统计次数。", source:"来源：Linux 日志排查（自编练习）" },
      { id:"DL-lnx-20", type:"cmd", q:"写出命令：统计 /var/log/secure 中登录失败的行数。", answerView:"grep -c \"Failed\" /var/log/secure（或 grep Failed /var/log/secure | wc -l）", analysis:"-c 直接计数；配合 lastb 可交叉验证。", source:"来源：Linux 日志排查（自编练习）" },
      { id:"DL-lnx-21", type:"fill", q:"补全：查看当前用户的定时任务列表命令是 crontab ＿＿＿。", answer:"-l", alts:["-l"], answerView:"crontab -l", analysis:"-e 编辑、-l 列出、-r 删除。", source:"来源：Linux 计划任务与日志（自编练习）" },
      { id:"DL-lnx-22", type:"choice", q:"查看内核启动与硬件相关信息，应使用？", options:[{key:"A",text:"dmesg"},{key:"B",text:"whoami"},{key:"C",text:"uname -a"},{key:"D",text:"以上都可看（dmesg 最直接）"}], answer:"A", answerView:"dmesg", analysis:"dmesg 显示内核环形缓冲区消息；uname -a 看内核版本。", source:"来源：Linux 日志与命令（自编练习）" },
      { id:"DL-lnx-23", type:"judge", q:"/var/log/lastlog、wtmp、btmp 都是二进制文件，不宜用 cat 直接查看。", answer:"T", answerView:"正确", analysis:"应使用 lastlog / last / lastb 等专用命令。", source:"来源：教材19.3.2（审计机制）" },
      { id:"DL-lnx-24", type:"group", q:"把下列命令归入对应用途：", left:[{k:"netstat -tlnp"},{k:"useradd"},{k:"grep Failed /var/log/secure"},{k:"find / -perm -4000"}], groups:["网络排查","账号管理","日志分析","文件排查"], answer:["网络排查","账号管理","日志分析","文件排查"], answerView:"netstat网络/useradd账号/grep日志/find文件", analysis:"按用途归类便于应急时快速取用。", source:"来源：Linux 日志与命令（自编练习）" },
      { id:"DL-lnx-25", type:"order", q:"请按入侵排查顺序排列（↑↓ 调整）：", steps:["查看网络连接与监听端口","查看可疑进程","查看登录与认证日志","查看文件与启动项变化","取证并留存证据"], shuffled:["查看可疑进程","查看网络连接与监听端口","查看文件与启动项变化","查看登录与认证日志","取证并留存证据"], answerView:"网络→进程→日志→文件/启动项→取证", analysis:"先动态易失信息（网络/进程），再日志与文件，最后固定证据。", source:"来源：教材17.5.6 入侵取证（易失信息优先）" },
      { id:"DL-lnx-26", type:"cmd", q:"写出命令：查看本机路由表（旧式命令）。", answerView:"route -n", analysis:"新式命令 ip route；查看网卡 ip addr。", source:"来源：Linux 网络排查命令（自编练习）" },
      { id:"DL-lnx-27", type:"fill", q:"补全：查看到目标主机 8.8.8.8 的逐跳路径命令是 traceroute ＿＿＿。", answer:"8.8.8.8", alts:["8.8.8.8"], answerView:"traceroute 8.8.8.8", analysis:"Windows 对应 tracert。", source:"来源：Linux 网络排查命令（自编练习）" },
      { id:"DL-lnx-28", type:"choice", q:"实时跟踪日志文件的新增内容，应使用？", options:[{key:"A",text:"tail -f 日志文件"},{key:"B",text:"head 日志文件"},{key:"C",text:"cat 日志文件"},{key:"D",text:"wc -l 日志文件"}], answer:"A", answerView:"tail -f", analysis:"-f 跟随文件增长；-n 100 查看最后 100 行。", source:"来源：Linux 日志与命令（自编练习）" },
      { id:"DL-lnx-29", type:"multi", q:"下列属于 Linux 应急排查常用命令的有？", options:[{key:"A",text:"netstat/ss"},{key:"B",text:"ps -ef"},{key:"C",text:"last/lastb"},{key:"D",text:"format C:"}], answer:["A","B","C"], answerView:"netstat/ss、ps、last/lastb", analysis:"format 是 Windows 磁盘命令，与排查无关。", source:"来源：教材17.5.6 入侵取证" },
      { id:"DL-lnx-30", type:"pair", q:"匹配命令与作用：", left:[{k:"ps -ef"},{k:"top"},{k:"df -h"},{k:"free -m"},{k:"du -sh"}], right:["查看全部进程","实时查看系统负载","查看磁盘使用率","查看内存使用","统计目录占用空间"], answer:["0","1","2","3","4"], answerView:"ps进程/top负载/df磁盘/free内存/du目录", analysis:"排查时先看资源与进程异常。", source:"来源：Linux 系统排查命令（自编练习）" },
      { id:"DL-lnx-31", type:"judge", q:"whoami 查看当前有效用户名，id 可查看 UID/GID 及所属组。", answer:"T", answerView:"正确", analysis:"id 比 whoami 信息更全。", source:"来源：Linux 账号与权限（自编练习）" },
      { id:"DL-lnx-30b", type:"choice", q:"要确认某个用户属于哪些组，应使用？", options:[{key:"A",text:"groups 用户名 / id 用户名"},{key:"B",text:"ls -l 用户名"},{key:"C",text:"cat 用户名"},{key:"D",text:"file 用户名"}], answer:"A", answerView:"groups / id", analysis:"组信息也可查看 /etc/group。", source:"来源：Linux 账号与权限（自编练习）" },
      { id:"DL-lnx-32", type:"blanks", q:"某主机疑似被入侵，补全排查命令（各一空）：", blanks:[{label:"查看监听端口", answer:"netstat -tlnp", alts:["netstat -tlnp","ss -tlnp"]},{label:"查看失败登录", answer:"lastb", alts:["lastb"]}], answerView:"netstat -tlnp；lastb", analysis:"端口与失败登录是最先看的两项。", source:"来源：教材17.5.6 入侵取证" },
      { id:"DL-lnx-33", type:"choice", q:"/etc/shadow 中保存的是？", options:[{key:"A",text:"明文口令"},{key:"B",text:"口令哈希及有效期信息"},{key:"C",text:"用户主目录"},{key:"D",text:"组信息"}], answer:"B", answerView:"口令哈希及口令有效期等", analysis:"哈希加盐存储；解密的密钥不存在。", source:"来源：2020下半年案例试题一 问题5" },
      { id:"DL-lnx-34", type:"fix", q:"下面命令有误，请改正（统计 secure 日志中失败登录次数）：\ngrep Failed /var/log/secure | wc", answerView:"grep Failed /var/log/secure | wc -l", analysis:"wc 需带 -l 才统计行数。", source:"来源：Linux 日志排查（自编练习）" },

      { id:"DL-perm-01", type:"choice", q:"权限属性 rwxr-xr-x 对应的数字表示是？", options:[{key:"A",text:"700"},{key:"B",text:"755"},{key:"C",text:"644"},{key:"D",text:"777"}], answer:"B", answerView:"755", analysis:"r=4,w=2,x=1；owner=7、group=5、other=5。", source:"来源：2019上半年案例试题一 问题3（权限数字换算）" },
      { id:"DL-perm-02", type:"fill", q:"补全：属性 -rwx------ 的数字表示是 ＿＿＿。", answer:"700", alts:["700"], answerView:"700", analysis:"只有属主有 rwx（4+2+1=7），组与其他为 0。", source:"来源：2019上半年案例试题一 问题3" },
      { id:"DL-perm-03", type:"fill", q:"补全：属性 -rw-r--r-- 的数字表示是 ＿＿＿。", answer:"644", alts:["644"], answerView:"644", analysis:"属主 rw=6，组 r=4，其他 r=4。", source:"来源：Linux 权限换算（自编练习）" },
      { id:"DL-perm-04", type:"choice", q:"属性 -rwsr-xr-x 的数字表示是？", options:[{key:"A",text:"755"},{key:"B",text:"4755"},{key:"C",text:"2755"},{key:"D",text:"1755"}], answer:"B", answerView:"4755（SUID）", analysis:"s 位：SUID=4000、SGID=2000、SBIT=1000。", source:"来源：2022下半年案例试题二（SUID/符号链接）" },
      { id:"DL-perm-05", type:"calc", q:"已知 /etc/passwd 的权限是 -rw-r--r--，/etc/shadow 的权限是 -rw-------。请填空：", blanks:[{label:"passwd 数字权限", answer:"644", alts:["644"]},{label:"shadow 数字权限", answer:"600", alts:["600","400"]}], answerView:"passwd=644；shadow=600（或 400）", analysis:"shadow 仅 root 可读，常见 600 或 400。", source:"来源：2020下半年案例试题一 问题1（口令文件权限）" },
      { id:"DL-perm-06", type:"cmd", q:"写出命令：把文件 net.txt 的权限设为仅属主可读写执行。", answerView:"chmod 700 net.txt", analysis:"等价于 chmod u=rwx,go= net.txt。", source:"来源：2019上半年案例试题一 问题3" },
      { id:"DL-perm-07", type:"cmd", q:"写出命令：去掉目录 dir 上所有用户的执行（进入）权限。", answerView:"chmod a-x dir", analysis:"a 表示 all（u/g/o）；去掉执行位后无法 cd 进入。", source:"来源：教材19.3.6 Linux 安全增强配置参考" },
      { id:"DL-perm-08", type:"pair", q:"匹配权限位与数值：", left:[{k:"r"},{k:"w"},{k:"x"},{k:"SUID"},{k:"SBIT"}], right:["4","2","1","4000","1000"], answer:["0","1","2","3","4"], answerView:"r=4/w=2/x=1/SUID=4000/SBIT=1000", analysis:"SGID=2000；粘滞位常用于 /tmp。", source:"来源：Linux 权限换算（自编练习）" },
      { id:"DL-perm-09", type:"judge", q:"umask 为 022 时，新建目录的默认权限是 755，新建文件是 644。", answer:"T", answerView:"正确", analysis:"目录默认 777-umask，文件默认 666-umask。", source:"来源：Linux 权限换算（自编练习）" },
      { id:"DL-perm-10", type:"choice", q:"修改文件属主属组的命令是？", options:[{key:"A",text:"chmod"},{key:"B",text:"chown"},{key:"C",text:"chattr"},{key:"D",text:"umask"}], answer:"B", answerView:"chown（chgrp 改组）", analysis:"chown user:group file；-R 递归。", source:"来源：Linux 权限管理（自编练习）" },
      { id:"DL-perm-11", type:"fill", q:"补全：把文件 a.txt 设为任何人可读写（慎用），数字权限为 ＿＿＿。", answer:"666", alts:["666"], answerView:"666", analysis:"生产环境不应对可执行/敏感文件开放全局写。", source:"来源：Linux 权限换算（自编练习）" },
      { id:"DL-perm-12", type:"group", q:"把下列权限值归入对应含义：", left:[{k:"755"},{k:"644"},{k:"4755"},{k:"600"}], groups:["属主全权/其他只读执行","属主读写/其他只读","带SUID的可执行文件","仅属主读写"], answer:["属主全权/其他只读执行","属主读写/其他只读","带SUID的可执行文件","仅属主读写"], answerView:"755/644/4755/600", analysis:"记牢四组常见值即可应对多数考点。", source:"来源：Linux 权限换算（自编练习）" }
    ]
  },
  "U3.3.4": {
    topic: "RSA 密码计算",
    items: [
      { id:"DL-rsa-01", type:"choice", q:"RSA 算法的安全性主要基于哪类数学难题？", options:[{key:"A",text:"大整数因子分解"},{key:"B",text:"离散对数"},{key:"C",text:"背包问题"},{key:"D",text:"椭圆曲线"}], answer:"A", answerView:"大整数因子分解难题", analysis:"RSA 基于大整数分解；ECC 基于椭圆曲线离散对数。", source:"来源：2020下半年案例试题二 问题2" },
      { id:"DL-rsa-02", type:"choice", q:"RSA 的参数中，可以公开的是？", options:[{key:"A",text:"p、q"},{key:"B",text:"φ(n)、d"},{key:"C",text:"n、e"},{key:"D",text:"p、d"}], answer:"C", answerView:"n、e（公钥）", analysis:"p、q、φ(n)、d 必须保密，任一泄露都会导致私钥泄露。", source:"来源：2020下半年案例试题二 问题2" },
      { id:"DL-rsa-03", type:"calc", q:"已知 p=47、q=71、e=3，请计算：", blanks:[{label:"n =", answer:"3337", alts:["3337"]},{label:"φ(n) =", answer:"3220", alts:["3220"]},{label:"d =", answer:"2147", alts:["2147"]}], answerView:"n=3337、φ(n)=3220、d=2147", analysis:"n=47×71=3337；φ(n)=46×70=3220；由 3×d≡1 mod 3220 得 d=2147。", source:"来源：2022下半年案例试题四 问题5（RSA 加密）" },
      { id:"DL-rsa-04", type:"calc", q:"已知公钥 (n,e)=(55,3)，请计算：", blanks:[{label:"p、q", answer:"5和11", alts:["5和11","5,11","5 11","11和5"]},{label:"φ(n) =", answer:"40", alts:["40"]},{label:"私钥 d =", answer:"27", alts:["27"]}], answerView:"p=5,q=11；φ(n)=40；d=27", analysis:"55=5×11；φ=4×10=40；3×27=81=2×40+1。", source:"来源：2020下半年案例试题二 问题4（求私钥）" },
      { id:"DL-rsa-05", type:"calc", q:"用公钥 (55,3) 加密明文 m=18，求密文 c（写出算式）。", blanks:[{label:"c =", answer:"2", alts:["2"]}], answerView:"c = 18³ mod 55 = 5832 mod 55 = 2", analysis:"18³=5832；5832÷55=106 余 2。", source:"来源：2020下半年案例试题二 问题3（密文计算）" },
      { id:"DL-rsa-06", type:"judge", q:"RSA 中加密与解密使用不同密钥，因此公钥加密的内容只能用私钥解密。", answer:"T", answerView:"正确", analysis:"这对“双密钥”特性正是数字签名的实现基础。", source:"来源：2020下半年案例试题二 问题5" },
      { id:"DL-rsa-07", type:"choice", q:"使用 RSA 加密时，明文 m 必须满足？", options:[{key:"A",text:"m 为偶数"},{key:"B",text:"m < n"},{key:"C",text:"m 为素数"},{key:"D",text:"m > n"}], answer:"B", answerView:"m 的数值必须小于模数 n", analysis:"若 m ≥ n 则无法唯一还原，需分组或按字符逐个加密。", source:"来源：2022下半年案例试题四 问题5" },
      { id:"DL-rsa-08", type:"choice", q:"用 RSA 实现数字签名，正确的做法是？", options:[{key:"A",text:"用公钥加密、私钥解密"},{key:"B",text:"用私钥加密（签名）、公钥验证"},{key:"C",text:"双方使用同一密钥"},{key:"D",text:"只对消息哈希后异或"}], answer:"B", answerView:"私钥签名、公钥验证", analysis:"签名保证真实性与不可否认性；常对消息摘要签名以提高效率。", source:"来源：2020下半年案例试题二 问题7" },
      { id:"DL-rsa-09", type:"multi", q:"RSA 签名体制可以实现下列哪些安全目标？", options:[{key:"A",text:"真实性"},{key:"B",text:"保密性"},{key:"C",text:"完整性"},{key:"D",text:"可控性"}], answer:["A","B","C"], answerView:"真实性、保密性、完整性", analysis:"私钥签名保真实性、加密保保密性、哈希保完整性。", source:"来源：2020下半年案例试题二 问题8" },
      { id:"DL-rsa-10", type:"cmd", q:"写出 RSA 的加密与解密公式（用 m、c、e、d、n 表示）。", answerView:"加密：c = m^e mod n；解密：m = c^d mod n", analysis:"签名时用 d 运算、用 e 验证。", source:"来源：2020下半年案例试题二（公式默写）" },
      { id:"DL-rsa-11", type:"blanks", q:"计算下列模幂（各一空）：", blanks:[{label:"11×19 mod 26 =", answer:"1", alts:["1"]},{label:"18³ mod 55 =", answer:"2", alts:["2"]}], answerView:"209 mod 26=1；5832 mod 55=2", analysis:"模运算逐次取模可避免大数。", source:"来源：2019上半年案例试题二 问题1 / 2020下半年案例试题二 问题3" },
      { id:"DL-rsa-12", type:"order", q:"按 RSA 密钥生成与使用顺序排列（↑↓ 调整）：", steps:["选取大素数 p、q","计算 n=p×q 与 φ(n)=(p-1)(q-1)","选 e 且 gcd(e,φ(n))=1","由 e·d≡1 mod φ(n) 求 d","公开 (n,e)，保密 (p,q,d)"], shuffled:["计算 n=p×q 与 φ(n)=(p-1)(q-1)","选取大素数 p、q","由 e·d≡1 mod φ(n) 求 d","选 e 且 gcd(e,φ(n))=1","公开 (n,e)，保密 (p,q,d)"], answerView:"选素数→算n/φ→选e→求d→公开 (n,e)", analysis:"计算顺序是案例计算题的答题骨架。", source:"来源：2020下半年案例试题二" }
    ]
  },
  "U3.3.1": {
    topic: "DES 与对称密码",
    items: [
      { id:"DL-des-01", type:"choice", q:"DES 的分组长度与有效密钥长度分别是？", options:[{key:"A",text:"64 位分组、56 位有效密钥"},{key:"B",text:"128 位分组、64 位密钥"},{key:"C",text:"64 位分组、64 位密钥"},{key:"D",text:"128 位分组、128 位密钥"}], answer:"A", answerView:"64 位分组、56 位有效密钥", analysis:"密钥 64 位中 8 位为校验位，有效 56 位。", source:"来源：2017上半年案例试题四（DES 加密算法）" },
      { id:"DL-des-02", type:"fill", q:"补全：DES 对 64 位明文分组进行 ＿＿＿ 轮迭代运算。", answer:"16", alts:["16","十六"], answerView:"16 轮", analysis:"每轮使用一个 48 位子密钥，由 56 位密钥经置换选取得出。", source:"来源：教材3.3.1 DES" },
      { id:"DL-des-03", type:"choice", q:"DES 中“初始置换（IP）”的作用是？", options:[{key:"A",text:"按固定表对 64 位明文重新排列比特位"},{key:"B",text:"压缩密钥"},{key:"C",text:"产生子密钥"},{key:"D",text:"填充明文"}], answer:"A", answerView:"按 IP 表重排 64 位明文比特", analysis:"置换后分左右两半 L0/R0；末置换 IP⁻¹ 作用相反。", source:"来源：2017上半年案例试题四 问题3（初始置换表）" },
      { id:"DL-des-04", type:"calc", q:"若简化 DES 的初始置换表 IP 为：2 6 3 1 4 8 5 7（输出第1位取输入第2位…）。请填写逆置换 IP⁻¹ 中前 4 位：", blanks:[{label:"IP⁻¹(1..4)", answer:"4 1 3 5", alts:["4 1 3 5","4,1,3,5","4135"]}], answerView:"4 1 3 5（即 IP⁻¹ 表前四项）", analysis:"逆置换：原表第 i 位输出到位置 p，则逆表位置 p 填 i。", source:"来源：2017上半年案例试题四 问题4（求逆初始置换）" },
      { id:"DL-des-05", type:"choice", q:"DES 弱密钥指的是？", options:[{key:"A",text:"长度为 0 的密钥"},{key:"B",text:"使加密与解密结果相同的密钥（子密钥全相同）"},{key:"C",text:"含重复字符的密钥"},{key:"D",text:"由口令直接生成的密钥"}], answer:"B", answerView:"加密与解密结果相同的密钥", analysis:"弱密钥导致多轮子密钥相同，安全性大幅降低。", source:"来源：2017上半年案例试题四 问题5（弱密钥定义）" },
      { id:"DL-des-06", type:"judge", q:"DES 的 S 盒是唯一的非线性部件，是 DES 安全性的关键。", answer:"T", answerView:"正确", analysis:"S 盒把 48 位压缩为 32 位并做非线性代换。", source:"来源：2017上半年案例试题四 问题1-2（S 盒）" },
      { id:"DL-des-07", type:"choice", q:"为解决 DES 密钥过短问题，可以采用？", options:[{key:"A",text:"3DES（三重 DES）"},{key:"B",text:"更长的明文分组"},{key:"C",text:"增加 S 盒"},{key:"D",text:"减少轮数"}], answer:"A", answerView:"3DES（或 AES 等更强算法）", analysis:"3DES 用三次 DES 提升强度；AES 分组 128、密钥 128/192/256。", source:"来源：教材3.3.1 DES / 3.3.2" },
      { id:"DL-des-08", type:"pair", q:"匹配对称密码术语与含义：", left:[{k:"分组密码"},{k:"流密码"},{k:"S 盒"},{k:"子密钥"},{k:"初始置换"}], right:["按固定长度分组逐组加密","按比特/字节流逐位加密","非线性代换部件","每轮使用的派生密钥","加密前的比特重排"], answer:["0","1","2","3","4"], answerView:"分组/流/S盒/子密钥/初始置换", analysis:"DES 属分组密码；RC4 属流密码。", source:"来源：教材3.2 密码体制分类 / 3.3.1" }
    ]
  },
  "U3.3": {
    topic: "仿射密码与分组工作模式",
    items: [
      { id:"DL-aff-01", type:"choice", q:"仿射密码属于哪一类密码？", options:[{key:"A",text:"非对称密码"},{key:"B",text:"古典对称密码（代换密码）"},{key:"C",text:"哈希算法"},{key:"D",text:"公钥算法"}], answer:"B", answerView:"古典对称代换密码", analysis:"加密 e(x)=(k1·x+k2) mod 26。", source:"来源：2019上半年案例试题二（仿射密码）" },
      { id:"DL-aff-02", type:"calc", q:"仿射密码密钥 key=(11,3)，字母编号 A=0…Z=25。请计算：", blanks:[{label:"11 在 Z26 中的乘法逆元", answer:"19", alts:["19"]},{label:"明文 SEC 的密文", answer:"TVZ", alts:["TVZ"]}], answerView:"11⁻¹=19；SEC→TVZ", analysis:"S(18)→(11×18+3) mod 26=19→T；E(4)→47 mod 26=21→V；C(2)→25→Z。", source:"来源：2019上半年案例试题二 问题2" },
      { id:"DL-aff-03", type:"choice", q:"仿射密码中，密钥 k1 必须满足的条件是？", options:[{key:"A",text:"k1 与 26 互素（gcd=1）"},{key:"B",text:"k1 为偶数"},{key:"C",text:"k1=0"},{key:"D",text:"k1>26"}], answer:"A", answerView:"gcd(k1,26)=1", analysis:"只有与 26 互素才有乘法逆元、才能解密。", source:"来源：2019上半年案例试题二 问题2" },
      { id:"DL-aff-04", type:"choice", q:"分组密码工作模式中，相同明文分组会产生相同密文分组的是？", options:[{key:"A",text:"ECB"},{key:"B",text:"CBC"},{key:"C",text:"CFB"},{key:"D",text:"OFB"}], answer:"A", answerView:"ECB（电子密码本）", analysis:"ECB 无链路，相同明文→相同密文，易暴露数据模式。", source:"来源：教材3.3 常见密码算法（分组模式）" },
      { id:"DL-aff-05", type:"multi", q:"下列属于对称密码算法的有？", options:[{key:"A",text:"DES/3DES"},{key:"B",text:"AES"},{key:"C",text:"SM4"},{key:"D",text:"RSA"}], answer:["A","B","C"], answerView:"DES/3DES、AES、SM4", analysis:"RSA 为非对称；SM2 为非对称、SM3 为哈希。", source:"来源：教材3.2 密码体制分类" },
      { id:"DL-aff-06", type:"calc", q:"已知仿射加密中明文 E 对应密文 C、明文 T 对应密文 F（A=0…Z=25）。求密钥：", blanks:[{label:"k1 =", answer:"7", alts:["7"]},{label:"k2 =", answer:"24", alts:["24"]}], answerView:"k1=7、k2=24", analysis:"E=4→C=2；T=19→F=5；联立 4k1+k2≡2、19k1+k2≡5 (mod 26) 解得 k1=7、k2=24。", source:"来源：2019上半年案例试题二 问题3" },
      { id:"DL-aff-07", type:"judge", q:"CBC 模式需要初始向量 IV，且相同的明文分组在不同位置会得到不同密文。", answer:"T", answerView:"正确", analysis:"CBC 通过链接与 IV 消除相同明文→相同密文的问题。", source:"来源：教材3.3（分组模式）" },
      { id:"DL-aff-08", type:"pair", q:"匹配分组模式与特点：", left:[{k:"ECB"},{k:"CBC"},{k:"CFB"},{k:"OFB"},{k:"CTR"}], right:["最简单、相同明文得相同密文","需 IV、链式反馈、常用","密文反馈、可流式","输出反馈、可预处理","计数器模式、可并行"], answer:["0","1","2","3","4"], answerView:"ECB/CBC/CFB/OFB/CTR 的特点", analysis:"记忆口诀：ECB 无链、CBC 链密文、CFB 链密文流、OFB 链输出、CTR 用计数器。", source:"来源：教材3.3（分组模式）" }
    ]
  },
  "U3.4": {
    topic: "Hash 函数与数字签名",
    items: [
      { id:"DL-hash-01", type:"multi", q:"哈希函数 f 通常需要满足哪些性质？", options:[{key:"A",text:"单向性"},{key:"B",text:"抗弱碰撞性"},{key:"C",text:"抗强碰撞性"},{key:"D",text:"可逆性"}], answer:["A","B","C"], answerView:"单向性、抗弱碰撞性、抗强碰撞性", analysis:"哈希不可逆，故不含“可逆性”。", source:"来源：2019上半年案例试题三 问题3" },
      { id:"DL-hash-02", type:"choice", q:"“找到任何满足 f(x)=f(y) 的偶对 (x,y) 在计算上不可行”描述的是？", options:[{key:"A",text:"单向性"},{key:"B",text:"抗弱碰撞性"},{key:"C",text:"抗强碰撞性"},{key:"D",text:"可逆性"}], answer:"C", answerView:"抗强碰撞性", analysis:"注意：题目说“任何一对”即强碰撞；给定 x 找 y 为弱碰撞。", source:"来源：2019上半年案例试题三 问题3" },
      { id:"DL-hash-03", type:"judge", q:"数字签名通常先对消息求哈希再签名，这样既提高效率又能保证完整性。", answer:"T", answerView:"正确", analysis:"哈希把任意长度压缩为固定摘要，签名只对小摘要运算。", source:"来源：教材3.4 Hash函数与数字签名" },
      { id:"DL-hash-04", type:"pair", q:"匹配安全目标与实现手段：", left:[{k:"保密性"},{k:"完整性"},{k:"真实性/不可否认性"},{k:"可用性"}], right:["加密（对称/非对称）","哈希摘要","数字签名","冗余与备份、限流防护"], answer:["0","1","2","3"], answerView:"加密保保密、哈希保完整、签名保真实、冗余保可用", analysis:"案例题常考“用什么技术实现什么目标”。", source:"来源：2020下半年案例试题二 问题8" }
    ]
  },
  "U7.1": {
    topic: "访问控制概述",
    items: [
      { id:"DL-ac-01", type:"choice", q:"针对信息系统的访问控制包含哪三个基本要素？", options:[{key:"A",text:"主体、客体、授权访问"},{key:"B",text:"用户、口令、权限"},{key:"C",text:"身份、角色、资源"},{key:"D",text:"网络、主机、应用"}], answer:"A", answerView:"主体、客体、授权访问（顺序无关）", analysis:"主体=发起访问者；客体=被访问资源；授权访问=控制策略。", source:"来源：2019上半年案例试题一 问题1 / 2024下半年案例试题一" },
      { id:"DL-ac-02", type:"judge", q:"访问控制是在身份认证的基础上，对用户提出的资源访问请求加以控制。", answer:"T", answerView:"正确", analysis:"先认证身份，再按策略授权（认证→授权→审计）。", source:"来源：2019上半年案例试题一（说明部分）" },
      { id:"DL-ac-03", type:"choice", q:"访问控制的主要任务是？", options:[{key:"A",text:"保证系统资源不被非法使用和非常规访问"},{key:"B",text:"提高网络带宽"},{key:"C",text:"压缩数据"},{key:"D",text:"备份数据库"}], answer:"A", answerView:"保证资源不被非法使用和非常规访问", analysis:"核心是“最小权限 + 授权使用”。", source:"来源：2019上半年案例试题一" },
      { id:"DL-ac-04", type:"fill", q:"补全三要素：访问控制由 ＿＿＿、客体和授权访问三个基本要素构成。", answer:"主体", alts:["主体"], answerView:"主体", analysis:"主体如用户、进程；客体如文件、数据库、设备。", source:"来源：2019上半年案例试题一 问题1" },
      { id:"DL-ac-05", type:"judge", q:"“最小权限原则”要求只授予完成工作所必需的最小权限。", answer:"T", answerView:"正确", analysis:"是最小权限、职责分离等安全原则在访问控制中的体现。", source:"来源：教材7.1.2 访问控制目标" },
      { id:"DL-ac-06", type:"choice", q:"访问控制策略的实现方式主要有？", options:[{key:"A",text:"访问控制表、能力表、访问控制矩阵"},{key:"B",text:"加密、解密、哈希"},{key:"C",text:"备份、恢复、容灾"},{key:"D",text:"扫描、渗透、加固"}], answer:"A", answerView:"ACL、能力表、访问控制矩阵", analysis:"三者的区别是案例与选择题的高频考点。", source:"来源：2016下半年案例试题二（访问控制实现方法）" }
    ]
  },
  "U7.2": {
    topic: "访问控制模型（DAC/MAC/RBAC/BLP/Biba）",
    items: [
      { id:"DL-acm-01", type:"choice", q:"由资源属主自主决定把权限授予谁，属于哪种访问控制？", options:[{key:"A",text:"自主访问控制 DAC"},{key:"B",text:"强制访问控制 MAC"},{key:"C",text:"基于角色的访问控制 RBAC"},{key:"D",text:"基于任务的访问控制"}], answer:"A", answerView:"自主访问控制 DAC", analysis:"DAC 灵活但易被越权传播；MAC 由系统按安全标签强制控制。", source:"来源：教材7.2 访问控制模型" },
      { id:"DL-acm-02", type:"choice", q:"BLP 模型主要保证信息的？", options:[{key:"A",text:"机密性"},{key:"B",text:"完整性"},{key:"C",text:"可用性"},{key:"D",text:"真实性"}], answer:"A", answerView:"机密性", analysis:"BLP：下读上写（no read up / no write down）。", source:"来源：2019上半年案例试题一 问题2 / 2025下半年案例试题四" },
      { id:"DL-acm-03", type:"choice", q:"BLP 模型的访问控制策略是？", options:[{key:"A",text:"上读下写"},{key:"B",text:"下读上写"},{key:"C",text:"下读下写"},{key:"D",text:"上读上写"}], answer:"B", answerView:"下读上写", analysis:"简单安全规则：低级别主体不能读高级别客体（不下读）；星规则：不能下写。", source:"来源：2019上半年案例试题一 问题2" },
      { id:"DL-acm-04", type:"choice", q:"与 BLP 相反、主要用于保证完整性的模型是？", options:[{key:"A",text:"Biba 模型"},{key:"B",text:"BLP 模型"},{key:"C",text:"Clark-Wilson 模型"},{key:"D",text:"中国墙模型"}], answer:"A", answerView:"Biba 模型（下写上读）", analysis:"Biba 保证完整性：低完整级主体不能写高完整级客体（不下写）。", source:"来源：教材7.2.2 访问控制模型发展" },
      { id:"DL-acm-05", type:"choice", q:"以“角色”为核心、把权限赋予角色再把角色赋予用户的模型是？", options:[{key:"A",text:"DAC"},{key:"B",text:"MAC"},{key:"C",text:"RBAC"},{key:"D",text:"BLP"}], answer:"C", answerView:"RBAC（基于角色的访问控制）", analysis:"RBAC 支持角色继承与职责分离，适合企业授权管理。", source:"来源：教材7.2 访问控制模型" },
      { id:"DL-acm-06", type:"judge", q:"强制访问控制（MAC）中，主体和客体都有安全级别标签，访问由系统按标签规则强制判定。", answer:"T", answerView:"正确", analysis:"MAC 用于军事等高安全场景，用户无法自主改变标签。", source:"来源：教材7.2 访问控制模型" },
      { id:"DL-acm-07", type:"pair", q:"匹配模型与核心特征：", left:[{k:"DAC"},{k:"MAC"},{k:"RBAC"},{k:"BLP"},{k:"Biba"}], right:["属主自主授权","系统按安全标签强制控制","权限绑定角色","保机密性(下读上写)","保完整性(下写上读)"], answer:["0","1","2","3","4"], answerView:"DAC/MAC/RBAC/BLP/Biba 的核心特征", analysis:"先分清 DAC-MAC-RBAC 三类，再看 BLP/Biba 的方向规则。", source:"来源：教材7.2 访问控制模型" },
      { id:"DL-acm-08", type:"choice", q:"以“主体”为索引、记录该主体可访问哪些客体的表是？", options:[{key:"A",text:"访问控制表 ACL"},{key:"B",text:"能力表 Capability List"},{key:"C",text:"访问控制矩阵"},{key:"D",text:"安全标签表"}], answer:"B", answerView:"能力表（以主体为核心）", analysis:"ACL 以客体为核心列出可访问的主体；矩阵是二者的二维展开。", source:"来源：2016下半年案例试题二（能力表/ACL/矩阵）" },
      { id:"DL-acm-09", type:"choice", q:"ACL（访问控制表）是以什么为核心组织权限的？", options:[{key:"A",text:"以客体为核心，列出可访问的主体及权限"},{key:"B",text:"以主体为核心，列出可访问的客体"},{key:"C",text:"以角色为核心"},{key:"D",text:"以时间为序"}], answer:"A", answerView:"以客体为核心", analysis:"ACL 常用于文件系统（如 Linux 的 rwx 与扩展 ACL）。", source:"来源：2016下半年案例试题二" },
      { id:"DL-acm-10", type:"group", q:"把下列特征归入对应模型：", left:[{k:"属主可自行授权"},{k:"安全级别标签强制控制"},{k:"权限赋予角色"},{k:"军事机密场景常用"}], groups:["DAC","MAC","RBAC"], answer:["DAC","MAC","RBAC","MAC"], answerView:"自主任意→DAC；标签强制/军事→MAC；角色→RBAC", analysis:"归类题常考“谁决定授权”。", source:"来源：教材7.2 访问控制模型" }
    ]
  },
  "U7.3": {
    topic: "访问控制类型与实现",
    items: [
      { id:"DL-act-01", type:"judge", q:"访问控制矩阵的行对应主体、列对应客体，矩阵元素是访问权限。", answer:"T", answerView:"正确", analysis:"按行看即能力表，按列看即 ACL。", source:"来源：2016下半年案例试题二" },
      { id:"DL-act-02", type:"choice", q:"Linux 中 /etc/passwd 的属主为 root、权限 644，普通用户可对其进行？", options:[{key:"A",text:"读取"},{key:"B",text:"写入"},{key:"C",text:"删除"},{key:"D",text:"改属主"}], answer:"A", answerView:"只读", analysis:"644=属主 rw、组/其他只读。", source:"来源：2020下半年案例试题一 问题1" },
      { id:"DL-act-03", type:"fill", q:"补全：Linux 中把文件授权给其他用户的机制除基本 rwx 外，还可用扩展 ＿＿＿。", answer:"ACL", alts:["acl","ACL"], answerView:"扩展 ACL（setfacl/getfacl）", analysis:"setfacl -m u:user:rw file 授权；getfacl 查看。", source:"来源：教材7.7 访问控制技术应用" },
      { id:"DL-act-04", type:"choice", q:"RBAC 中“职责分离”的主要目的是？", options:[{key:"A",text:"防止单人拥有过多权限造成风险"},{key:"B",text:"提升网络速度"},{key:"C",text:"减少存储占用"},{key:"D",text:"简化口令"}], answer:"A", answerView:"防止权限过度集中", analysis:"如“制单”与“审核”必须由不同角色承担。", source:"来源：教材7.2 访问控制模型" },
      { id:"DL-act-05", type:"judge", q:"能力表难以撤销已发放的能力，而 ACL 便于按客体集中管理权限。", answer:"T", answerView:"正确", analysis:"两者各有优劣，实际系统常结合使用（如 ACL 为主）。", source:"来源：2016下半年案例试题二" },
      { id:"DL-act-06", type:"blanks", q:"补全：把 /home/test 目录及其内容授权给用户 tom 读写，使用扩展 ACL 的命令（两空）：", blanks:[{label:"授权命令", answer:"setfacl -R -m u:tom:rw /home/test", alts:["setfacl -R -m u:tom:rw /home/test","setfacl -m u:tom:rw /home/test"]},{label:"查看命令", answer:"getfacl /home/test", alts:["getfacl /home/test"]}], answerView:"setfacl -R -m u:tom:rw /home/test；getfacl /home/test", analysis:"-R 递归、-m 修改、u:用户:权限。", source:"来源：教材7.7 访问控制技术应用" }
    ]
  },
  "U2.3.3": {
    topic: "C 语言缓冲区溢出漏洞",
    items: [
      { id:"DL-bof-01", type:"choice", q:"下列哪个 C 函数不检查输入长度，最容易造成栈溢出？", options:[{key:"A",text:"fgets"},{key:"B",text:"gets"},{key:"C",text:"strncpy"},{key:"D",text:"snprintf"}], answer:"B", answerView:"gets（不检查长度，危险）", analysis:"gets 已废弃；安全替代为 fgets。", source:"来源：2016下半年案例试题五（gets 溢出）" },
      { id:"DL-bof-02", type:"choice", q:"栈溢出的本质是？", options:[{key:"A",text:"向栈上的局部数组写入超过其长度的数据，覆盖相邻数据"},{key:"B",text:"磁盘空间不足"},{key:"C",text:"内存条损坏"},{key:"D",text:"CPU 主频过低"}], answer:"A", answerView:"越界写入覆盖栈上相邻数据（如返回地址）", analysis:"若覆盖函数返回地址，可劫持程序执行流。", source:"来源：2020下半年案例试题五（栈溢出）" },
      { id:"DL-bof-03", type:"fill", q:"补全：溢出时若覆盖了函数栈帧中的 ＿＿＿，攻击者可控制程序跳转。", answer:"返回地址", alts:["返回地址","ret","eip"], answerView:"返回地址（RET/EIP）", analysis:"这也是“代码注入执行”的关键。", source:"来源：2020下半年案例试题五" },
      { id:"DL-bof-04", type:"choice", q:"MSVC 的 /GS 编译选项的作用是？", options:[{key:"A",text:"在栈中插入“安全 cookie”，返回前校验以检测溢出"},{key:"B",text:"加密源代码"},{key:"C",text:"压缩可执行文件"},{key:"D",text:"禁用内存"}], answer:"A", answerView:"栈 cookie 检测（栈保护）", analysis:"除 /GS 外还有 DEP(NX)、ASLR 等缓解机制。", source:"来源：2020下半年案例试题五 问题3（安全编译选项）" },
      { id:"DL-bof-05", type:"multi", q:"下列属于缓冲区溢出缓解/防护措施的有？", options:[{key:"A",text:"/GS 栈保护"},{key:"B",text:"DEP/NX 数据执行保护"},{key:"C",text:"ASLR 地址空间布局随机化"},{key:"D",text:"关闭所有日志"}], answer:["A","B","C"], answerView:"/GS、DEP、ASLR", analysis:"另有 SafeSEH、CFG 等；关闭日志与防护无关。", source:"来源：2020下半年案例试题五 问题3" },
      { id:"DL-bof-06", type:"cmd", q:"把不安全调用 fgets 之外，请写出替代 gets(buf) 的安全写法（buf 大小 64）。", answerView:"fgets(buf, sizeof(buf), stdin);", analysis:"限定读取长度并指定流；也可用 scanf 的宽度限定 %63s。", source:"来源：2016下半年案例试题五（溢出修复）" },
      { id:"DL-bof-07", type:"judge", q:"C 语言编译器默认会对数组下标做越界检查。", answer:"F", answerView:"错误（不检查，需开发者自行控制）", analysis:"这正是 C 语言易发生缓冲区溢出的根本原因。", source:"来源：2020下半年案例试题五 问题1" },
      { id:"DL-bof-08", type:"pair", q:"匹配防护机制与作用：", left:[{k:"/GS"},{k:"DEP/NX"},{k:"ASLR"},{k:"SafeSEH"},{k:"CFG"}], right:["栈 cookie 校验","数据页不可执行","内存地址随机化","异常处理链保护","控制流完整性校验"], answer:["0","1","2","3","4"], answerView:"/GS 栈保护、DEP 不可执行、ASLR 随机化、SafeSEH、CFG", analysis:"多选题常考“哪些属于溢出防护”。", source:"来源：2020下半年案例试题五 问题3" },
      { id:"DL-bof-09", type:"order", q:"按栈溢出利用过程排列（↑↓ 调整）：", steps:["程序接收超长输入","局部数组越界写入","覆盖栈上保存的返回地址","函数返回时跳转到攻击者指定地址","执行攻击代码（或崩溃）"], shuffled:["局部数组越界写入","程序接收超长输入","函数返回时跳转到攻击者指定地址","覆盖栈上保存的返回地址","执行攻击代码（或崩溃）"], answerView:"超长输入→越界写→覆盖返回地址→跳转→执行", analysis:"理解该链条即可作答原理与危害类小题。", source:"来源：2020下半年案例试题五" },
      { id:"DL-bof-10", type:"choice", q:"下列函数中相对安全、不易溢出的有？", options:[{key:"A",text:"strcpy / strcat"},{key:"B",text:"strncpy / strncat / snprintf"},{key:"C",text:"gets"},{key:"D",text:"sprintf"}], answer:"B", answerView:"strncpy / strncat / snprintf", analysis:"带 n 或限定长度的版本更安全，但仍需注意边界。", source:"来源：2016下半年案例试题五" },
      { id:"DL-bof-11", type:"choice", q:"下列哪个函数用于内存拷贝且不检查长度？", options:[{key:"A",text:"memcpy"},{key:"B",text:"memcpy_s"},{key:"C",text:"strlcpy"},{key:"D",text:"snprintf"}], answer:"A", answerView:"memcpy（memcpy_s 为安全版本）", analysis:"memcpy 需自行保证长度正确。", source:"来源：C 语言代码漏洞（自编练习）" },
      { id:"DL-bof-12", type:"judge", q:"模糊测试（Fuzzing）可通过对输入随机扰动来发现溢出类漏洞。", answer:"T", answerView:"正确", analysis:"Fuzzing 属黑盒测试，可能有漏报但能发现部分异常。", source:"来源：2018上半年案例试题二 问题3（模糊测试）" },
      { id:"DL-bof-13", type:"fill", q:"补全：溢出可能覆盖栈上保存的 EBP 与 RET，其中 EBP 通常指向 ＿＿＿。", answer:"栈帧基址", alts:["栈帧基址","帧指针","基址"], answerView:"栈帧基址（帧指针）", analysis:"EBP 定位局部变量与参数，RET 决定返回位置。", source:"来源：2020下半年案例试题五 问题2（变量与参数位置）" },
      { id:"DL-bof-14", type:"choice", q:"下列哪种做法不能从根本上避免溢出？", options:[{key:"A",text:"用带长度限制的函数替换 unsafe 函数"},{key:"B",text:"对输入做长度与字符合法性校验"},{key:"C",text:"把缓冲区定义得足够大但仍无长度校验"},{key:"D",text:"启用 /GS 与 DEP 等编译与系统防护"}], answer:"C", answerView:"仅扩大缓冲区、不加长度校验", analysis:"根本之道是“长度校验 + 安全函数 + 编译防护”。", source:"来源：C 语言代码漏洞防护（自编练习）" },
      { id:"DL-bof-15", type:"blanks", q:"补全：Linux 下可利用 ＿＿＿ 机制随机化栈与库的加载地址；Windows 对应机制为 ＿＿＿。", blanks:[{label:"Linux 机制", answer:"ASLR", alts:["ASLR","aslr"]},{label:"Windows 机制", answer:"ASLR", alts:["ASLR","aslr"]}], answerView:"ASLR（Windows 亦为 ASLR）", analysis:"ASLR 让攻击者难以预测目标地址。", source:"来源：C 语言代码漏洞防护（自编练习）" },
      { id:"DL-bof-16", type:"choice", q:"以下代码段最可能存在的问题是？\nchar buf[12]; gets(buf);", options:[{key:"A",text:"数组越界/栈溢出"},{key:"B",text:"内存泄漏"},{key:"C",text:"死循环"},{key:"D",text:"类型转换错误"}], answer:"A", answerView:"gets 不限制长度 → 溢出", analysis:"输入超过 11 个字符（含结尾符）即越界。", source:"来源：2016下半年案例试题五" }
    ]
  }
  ,
  "U6.2": {
    topic: "身份认证技术与 PKI",
    items: [
      { id:"DL-krb-01", type:"multi", q:"身份认证中，用于证明身份的依据通常分为哪几类？", options:[{key:"A",text:"你知道什么（口令）"},{key:"B",text:"你拥有什么（令牌/U盾）"},{key:"C",text:"你是什么（指纹等生物特征）"},{key:"D",text:"你的IP地址" }], answer:["A","B","C"], answerView:"所知 / 所有 / 所是", analysis:"三要素：口令、令牌、生物特征；IP 不能作为身份凭据。", source:"来源：2021下半年案例试题四（认证技术分类）" },
      { id:"DL-krb-02", type:"choice", q:"“口令 + 短信验证码”属于哪种认证？", options:[{key:"A",text:"单因素认证"},{key:"B",text:"双因素认证"},{key:"C",text:"三因素认证"},{key:"D",text:"无认证"}], answer:"B", answerView:"双因素认证（知道 + 拥有）", analysis:"两类不同凭据组合即为双因素；两个口令不算双因素。", source:"来源：教材6.2 身份认证技术" },
      { id:"DL-krb-03", type:"fill", q:"补全：Kerberos 通过可信第三方 ＿＿＿（含 AS 与 TGS）发放票据完成认证。", answer:"KDC", alts:["KDC","密钥分发中心"], answerView:"KDC（密钥分发中心）", analysis:"AS 发放 TGT，TGS 用 TGT 换服务票据。", source:"来源：2021下半年案例试题四（Kerberos）" },
      { id:"DL-krb-04", type:"choice", q:"PKI 中最核心、负责签发和管理数字证书的实体是？", options:[{key:"A",text:"CA 认证机构"},{key:"B",text:"RA 注册机构"},{key:"C",text:"终端用户"},{key:"D",text:"证书库"}], answer:"A", answerView:"CA（认证机构）", analysis:"RA 负责受理审核，CA 负责签发/吊销。", source:"来源：教材6.3 公钥基础设施 PKI" },
      { id:"DL-krb-05", type:"fill", q:"补全：数字证书遵循的国际标准是 X.＿＿＿。", answer:"509", alts:["509","X.509"], answerView:"X.509", analysis:"X.509 定义证书格式与字段（版本、序列号、有效期、公钥、签名等）。", source:"来源：教材6.3.2 X.509 数字证书" },
      { id:"DL-krb-06", type:"choice", q:"数字信封的实现方式是？", options:[{key:"A",text:"用对称密钥加密数据，再用接收方公钥加密该对称密钥"},{key:"B",text:"用接收方公钥加密全部数据"},{key:"C",text:"用私钥加密全部数据"},{key:"D",text:"只做哈希" }], answer:"A", answerView:"对称加密数据 + 公钥加密对称密钥", analysis:"兼顾效率与密钥安全分发，是混合密码体制的典型应用。", source:"来源：2018下半年案例试题（数字信封）" },
      { id:"DL-krb-07", type:"judge", q:"CRL 是证书吊销列表，用于发布已吊销但尚未过期的证书信息。", answer:"T", answerView:"正确", analysis:"相比 CRL，OCSP 提供在线实时查询。", source:"来源：教材6.3 公钥基础设施 PKI" },
      { id:"DL-krb-08", type:"pair", q:"匹配 PKI 组件与职责：", left:[{k:"CA"},{k:"RA"},{k:"证书库"},{k:"CRL"},{k:"OCSP"}], right:["签发与管理证书","受理并审核证书申请","集中存放证书供查询","公布已吊销证书","在线查询证书状态"], answer:["0","1","2","3","4"], answerView:"CA签发/RA审核/证书库存放/CRL吊销/OCSP在线查询", analysis:"PKI 五件套是选择题高频点。", source:"来源：教材6.3 公钥基础设施 PKI" }
    ]
  },
  "U6.3": {
    topic: "认证协议与应用（RADIUS/802.1x/TLS）",
    items: [
      { id:"DL-auth-01", type:"choice", q:"RADIUS 协议的特点包括？", options:[{key:"A",text:"基于 UDP，实现认证、授权、计费（AAA）"},{key:"B",text:"基于 TCP，只做认证"},{key:"C",text:"只做加密"},{key:"D",text:"只做审计" }], answer:"A", answerView:"基于 UDP 的 AAA 协议", analysis:"RADIUS 用 UDP（1812/1813），TACACS+ 用 TCP（49）。", source:"来源：教材6.3 认证协议" },
      { id:"DL-auth-02", type:"choice", q:"TACACS+ 与 RADIUS 的主要区别之一是？", options:[{key:"A",text:"TACACS+ 基于 TCP 且对报文整体加密"},{key:"B",text:"TACACS+ 基于 UDP"},{key:"C",text:"TACACS+ 不支持授权"},{key:"D",text:"TACACS+ 只能认证 Cisco 设备" }], answer:"A", answerView:"TACACS+ 基于 TCP，加密整个报文", analysis:"TACACS+ 分离认证/授权/计费，常用于网络设备管理。", source:"来源：教材6.3 认证协议" },
      { id:"DL-auth-03", type:"fill", q:"补全：IEEE 802.1x 是一种基于 ＿＿＿ 的接入认证机制（EAP over LAN）。", answer:"端口", alts:["端口","port"], answerView:"端口（Port-Based）", analysis:"未通过认证的端口只能传输认证报文。", source:"来源：教材13.3 无线局域网安全（802.1x）" },
      { id:"DL-auth-04", type:"order", q:"按 SSL/TLS 握手主要步骤排列（↑↓ 调整）：", steps:["客户端发送 ClientHello（随机数、套件）","服务器回应 ServerHello 与证书","客户端验证证书并生成预主密钥（用服务器公钥加密）","双方由随机数与预主密钥导出会话密钥","加密通信开始"], shuffled:["服务器回应 ServerHello 与证书","客户端发送 ClientHello（随机数、套件）","双方由随机数与预主密钥导出会话密钥","客户端验证证书并生成预主密钥（用服务器公钥加密）","加密通信开始"], answerView:"ClientHello→ServerHello/证书→验证并协商→导出会话密钥→加密通信", analysis:"证书验证失败则中止连接，防止中间人。", source:"来源：2018下半年案例试题（SSL 握手）" },
      { id:"DL-auth-05", type:"judge", q:"数字证书中包含了证书持有者的公钥，并由 CA 的私钥签名以保证其真实性。", answer:"T", answerView:"正确", analysis:"验证时用 CA 公钥验签，形成信任链。", source:"来源：教材6.3.2 X.509 数字证书" },
      { id:"DL-auth-06", type:"group", q:"把下列要素归入对应类别：", left:[{k:"X.509 证书"},{k:"AES 密钥"},{k:"CRL 列表"},{k:"会话密钥" }], groups:["PKI 体系", "对称密码应用"], answer:["PKI 体系","对称密码应用","PKI 体系","对称密码应用"], answerView:"证书/CRL 属 PKI；AES 密钥与会话密钥属对称密码", analysis:"会话密钥通常由 TLS 握手协商产生并用于对称加密。", source:"来源：教材6.3 公钥基础设施 PKI" },
      { id:"DL-auth-07", type:"blanks", q:"补全：Kerberos 认证中，客户端先向 AS 申请 ＿＿＿，再用它向 TGS 申请 ＿＿＿。", blanks:[{label:"第一张票据", answer:"TGT", alts:["TGT","票据授予票据"]},{label:"服务票据", answer:"服务票据", alts:["服务票据","Service Ticket","ST"]}], answerView:"先申请 TGT，再换取服务票据", analysis:"TGT 用于免重复输入口令，是 Kerberos 单点登录的基础。", source:"来源：2021下半年案例试题四（Kerberos）" },
      { id:"DL-auth-08", type:"choice", q:"PKI 中的“信任链”是指？", options:[{key:"A",text:"从根 CA 经中间 CA 到终端实体证书的逐级签名关系"},{key:"B",text:"用户之间的信任"},{key:"C",text:"同一证书的多次备份"},{key:"D",text:"证书与私钥的绑定" }], answer:"A", answerView:"根 CA → 中间 CA → 终端证书的逐级签名", analysis:"浏览器内置根 CA 证书，逐级验证到终端证书。", source:"来源：教材6.3 公钥基础设施 PKI" }
    ]
  },
  "U22.4": {
    topic: "Web 应用安全（注入/XSS/CSRF/上传）",
    items: [
      { id:"DL-web-01", type:"choice", q:"SQL 注入漏洞产生的根本原因是？", options:[{key:"A",text:"用户输入被当作 SQL 语句的一部分拼接执行"},{key:"B",text:"数据库版本过低"},{key:"C",text:"服务器内存不足"},{key:"D",text:"未使用 HTTPS" }], answer:"A", answerView:"用户输入未过滤即拼接进 SQL 并执行", analysis:"危害包括拖库、篡改、删除数据、绕过认证。", source:"来源：2021下半年案例试题一（SQL 注入）" },
      { id:"DL-web-02", type:"cmd", q:"补全/写出：利用登录框 SQL 注入绕过认证的经典“万能密码”输入（用户名字段）。", answerView:"' or 1=1 --（或 admin' or '1'='1）", analysis:"注释符使后续口令校验失效，登录条件恒真。", source:"来源：2021下半年案例试题一（万能密码）" },
      { id:"DL-web-03", type:"choice", q:"防御 SQL 注入最有效的方法是？", options:[{key:"A",text:"使用参数化查询（预编译语句）"},{key:"B",text:"隐藏报错信息"},{key:"C",text:"只允许 GET 请求"},{key:"D",text:"加大数据库内存" }], answer:"A", answerView:"参数化查询（预编译）", analysis:"另配合最小权限、类型校验、WAF 等纵深防御措施。", source:"来源：2022下半年案例试题四（SQL 注入防护）" },
      { id:"DL-web-04", type:"multi", q:"XSS 常见类型包括？", options:[{key:"A",text:"反射型"},{key:"B",text:"存储型"},{key:"C",text:"DOM 型"},{key:"D",text:"端口型" }], answer:["A","B","C"], answerView:"反射型 / 存储型 / DOM 型", analysis:"存储型危害最大，常出现在留言板、评论等持久化场景。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-05", type:"judge", q:"防御 XSS 的核心措施是：对所有输出到页面的不可信数据进行 HTML 编码（转义）。", answer:"T", answerView:"正确", analysis:"输入过滤 + 输出编码 + CSP 是常见组合。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-06", type:"choice", q:"CSRF（跨站请求伪造）的攻击前提主要是？", options:[{key:"A",text:"用户已登录目标站点，浏览器自动携带 Cookie"},{key:"B",text:"服务器未开 HTTPS"},{key:"C",text:"数据库未加密"},{key:"D",text:"使用了强口令" }], answer:"A", answerView:"受害者在目标站点的登录态（Cookie）被自动携带", analysis:"防御：CSRF Token、校验 Referer/Origin、SameSite Cookie。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-07", type:"pair", q:"匹配 Web 漏洞与典型防御措施：", left:[{k:"SQL 注入"},{k:"XSS"},{k:"CSRF"},{k:"文件上传"},{k:"命令注入"}], right:["参数化查询/预编译","输出编码/转义","CSRF Token 校验","白名单校验类型与后缀","过滤特殊字符、避免拼接执行"], answer:["0","1","2","3","4"], answerView:"注入→参数化；XSS→输出编码；CSRF→Token；上传→白名单；命令注入→过滤/避免拼接", analysis:"“漏洞—防御”配对是案例题高频形式。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-08", type:"choice", q:"文件上传漏洞的常见防护措施是？", options:[{key:"A",text:"白名单校验扩展名/MIME，上传目录禁止执行脚本，重命名文件"},{key:"B",text:"只校验前端 JavaScript"},{key:"C",text:"上传到 Web 根目录"},{key:"D",text:"允许任意后缀" }], answer:"A", answerView:"白名单 + 禁止执行 + 重命名（后端校验）", analysis:"仅前端校验可被绕过，必须服务端校验。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-09", type:"fill", q:"补全：目录遍历攻击常利用 ＿＿＿ 序列跳出网站根目录读取任意文件。", answer:"../", alts:["../","..\\"], answerView:"../（路径穿越）", analysis:"防御：规范化路径并校验是否越出根目录。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-10", type:"choice", q:"OWASP Top 10 是？", options:[{key:"A",text:"Web 应用最常见十大安全风险排行榜"},{key:"B",text:"十种编程语言"},{key:"C",text:"十种防火墙"},{key:"D",text:"十种加密算法" }], answer:"A", answerView:"Web 应用十大安全风险", analysis:"常考条目：注入、失效的身份认证、敏感数据泄露、XXE、访问控制失效等。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-11", type:"group", q:"把下列漏洞归入对应类别：", left:[{k:"SQL 注入"},{k:"反射型 XSS"},{k:"CSRF"},{k:"SSRF" }], groups:["注入类", "跨站类"], answer:["注入类","跨站类","跨站类","注入类"], answerView:"SQL 注入/SSRF 属注入；XSS/CSRF 属跨站", analysis:"分类有助于快速定位防护手段。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-12", type:"cmd", q:"写出 PHP 中防止 SQL 注入的正确做法（用 PDO 预处理举例）。", answerView:"$stmt = $pdo->prepare(\"SELECT * FROM users WHERE name = ?\"); $stmt->execute([$name]);", analysis:"用占位符绑定参数，避免字符串拼接。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-13", type:"judge", q:"水平越权指用户访问了同级其他用户的资源；垂直越权指普通用户获得了管理员权限。", answer:"T", answerView:"正确", analysis:"防御：服务端对每次请求做权限校验，不信任前端。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-14", type:"fill", q:"补全：防止 XSS 时，对输出到 HTML 上下文的数据应做 HTML ＿＿＿ 处理。", answer:"编码", alts:["编码","转义","escape"], answerView:"HTML 编码（转义）", analysis:"不同上下文（HTML/JS/URL/属性）需用对应的编码方式。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-15", type:"choice", q:"命令注入漏洞的成因是？", options:[{key:"A",text:"用户输入被拼接到系统命令中执行"},{key:"B",text:"磁盘写满"},{key:"C",text:"未启用日志"},{key:"D",text:"使用了 HTTPS" }], answer:"A", answerView:"输入拼接进系统命令被执行", analysis:"防御：避免拼接、使用白名单、最小权限运行。", source:"来源：教材22.4 Web 应用安全" },
      { id:"DL-web-16", type:"blanks", q:"某登录接口存在注入，请补全两条排查/处置要点（各一空）：", blanks:[{label:"首要修复措施", answer:"参数化查询", alts:["参数化查询","预编译","参数绑定"]},{label:"纵深防御组件", answer:"WAF", alts:["WAF","web应用防火墙","Web应用防火墙"]}], answerView:"参数化查询（根治）+ WAF（拦截）", analysis:"根治靠编码规范，WAF 只能作为补充。", source:"来源：2021下半年案例试题一 问题3" }
    ]
  }
  ,
  "U4.4.5": {
    topic: "信息安全标准（ISO/IEC 27000 系列）",
    items: [
      { id:"DL-std-01", type:"choice", q:"ISO/IEC 27001 标准的内容是？", options:[{key:"A",text:"信息安全管理体系（ISMS）要求，可用于认证"},{key:"B",text:"信息安全风险评估方法"},{key:"C",text:"密码算法规范"},{key:"D",text:"网络设备配置指南" }], answer:"A", answerView:"ISMS（信息安全管理体系）要求", analysis:"27001 是认证依据，27002 是控制措施实用规则。", source:"来源：2019上半年案例试题三（ISO 27000 系列）" },
      { id:"DL-std-02", type:"choice", q:"ISO/IEC 27002 标准的内容是？", options:[{key:"A",text:"信息安全控制措施实用规则（实施指南）"},{key:"B",text:"管理体系认证要求"},{key:"C",text:"风险评估方法论"},{key:"D",text:"业务连续性管理" }], answer:"A", answerView:"信息安全控制实用规则", analysis:"常与 27001 配套使用：27001 提要求，27002 给做法。", source:"来源：2019上半年案例试题三" },
      { id:"DL-std-03", type:"fill", q:"补全：负责信息安全风险管理的 ISO/IEC 标准编号是 ISO/IEC 270＿＿＿。", answer:"05", alts:["05","27005"], answerView:"ISO/IEC 27005", analysis:"27000 术语与概述、27001 要求、27002 控制措施、27005 风险管理。", source:"来源：教材4.4.5 信息安全管理体系标准" },
      { id:"DL-std-04", type:"choice", q:"ISO/IEC 15408《信息技术 安全技术 信息技术安全性评估准则》通常被称为？", options:[{key:"A",text:"CC（Common Criteria）"},{key:"B",text:"BS 7799"},{key:"C",text:"SSE-CMM"},{key:"D",text:"ISO 9001" }], answer:"A", answerView:"CC（通用评估准则）", analysis:"我国等同采用为 GB/T 18336；评估保证级 EAL1~EAL7。", source:"来源：2020下半年案例试题一（ISO/IEC 15408）" },
      { id:"DL-std-05", type:"judge", q:"我国网络安全等级保护基本要求的国家标准是 GB/T 22239。", answer:"T", answerView:"正确", analysis:"GB/T 22239-2019 即等保 2.0 的“基本要求”。", source:"来源：2021下半年案例试题二（等级保护 2.0）" },
      { id:"DL-std-06", type:"pair", q:"匹配标准与内容：", left:[{k:"ISO/IEC 27001"},{k:"ISO/IEC 27002"},{k:"ISO/IEC 27005"},{k:"ISO/IEC 15408"},{k:"GB/T 22239"}], right:["ISMS 要求（可认证）","信息安全控制实用规则","信息安全风险管理","信息技术安全评估准则(CC)","网络安全等级保护基本要求"], answer:["0","1","2","3","4"], answerView:"27001要求/27002控制/27005风险/15408评估/22239等保", analysis:"这一组编号是选择题必背。", source:"来源：教材4.4.5 信息安全管理体系标准" }
    ]
  },
  "U1.7": {
    topic: "网络安全法律法规",
    items: [
      { id:"DL-law-01", type:"choice", q:"《中华人民共和国网络安全法》的施行日期是？", options:[{key:"A",text:"2016年11月7日"},{key:"B",text:"2017年6月1日"},{key:"C",text:"2019年1月1日"},{key:"D",text:"2021年9月1日" }], answer:"B", answerView:"2017年6月1日", analysis:"2016年11月7日通过，2017年6月1日施行。", source:"来源：2019上半年案例试题二（网络安全法）" },
      { id:"DL-law-02", type:"fill", q:"补全：网络运营者应当留存网络日志不少于 ＿＿＿ 个月。", answer:"6", alts:["6","六"], answerView:"6 个月", analysis:"《网络安全法》第二十一条要求。", source:"来源：《网络安全法》第二十一条" },
      { id:"DL-law-03", type:"choice", q:"《中华人民共和国数据安全法》的施行日期是？", options:[{key:"A",text:"2020年1月1日"},{key:"B",text:"2021年9月1日"},{key:"C",text:"2021年11月1日"},{key:"D",text:"2022年1月1日" }], answer:"B", answerView:"2021年9月1日", analysis:"与《关键信息基础设施安全保护条例》同一天施行。", source:"来源：数据安全法" },
      { id:"DL-law-04", type:"choice", q:"《中华人民共和国个人信息保护法》的施行日期是？", options:[{key:"A",text:"2021年9月1日"},{key:"B",text:"2021年11月1日"},{key:"C",text:"2020年1月1日"},{key:"D",text:"2023年1月1日" }], answer:"B", answerView:"2021年11月1日", analysis:"与《数据安全法》《网络安全法》共同构成数据合规三大法。", source:"来源：个人信息保护法" },
      { id:"DL-law-05", type:"fill", q:"补全：《中华人民共和国密码法》自 ＿＿＿ 年 1 月 1 日起施行。", answer:"2020", alts:["2020"], answerView:"2020 年 1 月 1 日", analysis:"密码法规范密码应用与管理，区分核心/普通/商用密码。", source:"来源：2020下半年案例试题（密码法）" },
      { id:"DL-law-06", type:"multi", q:"关于网络安全等级保护，下列说法正确的有？", options:[{key:"A",text:"安全保护等级分为五级，一级最低、五级最高"},{key:"B",text:"第三级及以上系统一般需定期测评"},{key:"C",text:"等保 2.0 把云计算、移动互联、物联网、工控纳入"},{key:"D",text:"第一级系统必须每年测评一次" }], answer:["A","B","C"], answerView:"分级五级、三级以上测评、等保 2.0 覆盖新场景", analysis:"一级为自主保护级，通常不需强制测评。", source:"来源：2021下半年案例试题二（等级保护 2.0）" }
    ]
  },
  "U25.2": {
    topic: "移动终端与应用安全",
    items: [
      { id:"DL-mob-01", type:"choice", q:"Android 应用沙箱机制的基础是？", options:[{key:"A",text:"基于 Linux 的用户/进程隔离与权限模型"},{key:"B",text:"基于 Windows 组策略"},{key:"C",text:"基于 BIOS"},{key:"D",text:"基于浏览器 Cookie" }], answer:"A", answerView:"每个应用独立 UID + Linux 隔离", analysis:"应用间数据默认隔离，需通过权限/共享机制交互。", source:"来源：教材25.2 移动终端安全" },
      { id:"DL-mob-02", type:"judge", q:"iOS 采用沙盒机制，应用只能访问自身沙盒目录及系统授权资源。", answer:"T", answerView:"正确", analysis:"iOS 还通过代码签名与 App Store 审核强化管控。", source:"来源：教材25.2 移动终端安全" },
      { id:"DL-mob-03", type:"multi", q:"移动 App 常见安全风险包括？", options:[{key:"A",text:"反编译与代码逆向"},{key:"B",text:"本地存储敏感信息未加密"},{key:"C",text:"通信未做证书校验（可被中间人）"},{key:"D",text:"服务器硬盘转速低" }], answer:["A","B","C"], answerView:"逆向、明文存储、通信不安全等", analysis:"对策：加固/混淆、安全存储、证书绑定（SSL Pinning）。", source:"来源：2021下半年案例试题四（移动 App 安全）" },
      { id:"DL-mob-04", type:"fill", q:"补全：为防止 App 被反编译，常用手段是代码 ＿＿＿ 与加壳加固。", answer:"混淆", alts:["混淆","obfuscation"], answerView:"代码混淆（配合加壳/加固）", analysis:"混淆提高逆向成本，但不能根本阻止逆向。", source:"来源：2021下半年案例试题四（移动 App 安全）" }
    ]
  },
  "U1.3": {
    topic: "信息安全基本属性（CIA）",
    items: [
      { id:"DL-cia-01", type:"choice", q:"信息安全的三个基本属性（CIA）是？", options:[{key:"A",text:"保密性、完整性、可用性"},{key:"B",text:"真实性、可控性、抗抵赖性"},{key:"C",text:"机密性、可控性、可审查性"},{key:"D",text:"身份、权限、审计" }], answer:"A", answerView:"保密性(Confidentiality)、完整性(Integrity)、可用性(Availability)", analysis:"扩展属性还有可控性、不可否认性、真实性等。", source:"来源：2020下半年案例试题（信息安全三要素）" },
      { id:"DL-cia-02", type:"choice", q:"拒绝服务（DoS）攻击主要破坏信息的？", options:[{key:"A",text:"可用性"},{key:"B",text:"保密性"},{key:"C",text:"完整性"},{key:"D",text:"不可否认性" }], answer:"A", answerView:"可用性", analysis:"DoS 使系统无法正常提供服务。", source:"来源：教材1.3 信息安全基本属性" },
      { id:"DL-cia-03", type:"fill", q:"补全：篡改数据破坏的是信息的 ＿＿＿ 属性。", answer:"完整性", alts:["完整性"], answerView:"完整性", analysis:"哈希/数字签名用于检测完整性是否被破坏。", source:"来源：教材1.3 信息安全基本属性" }
    ]
  },
  "U12.1": {
    topic: "网络安全审计·安全管理与应急响应",
    items: [
      { id:"DL-sdlc-01", type:"choice", q:"在 SDLC（系统开发生命周期）中引入安全活动的主要目的？", options:[{key:"A",text:"在需求、设计、编码、测试、运维各阶段尽早发现并消除安全缺陷"},{key:"B",text:"缩短开发周期"},{key:"C",text:"降低硬件成本"},{key:"D",text:"减少测试用例" }], answer:"A", answerView:"把安全左移，各阶段消除安全缺陷", analysis:"安全左移可显著降低修复成本。", source:"来源：教材12.1 安全管理（安全工程）" },
      { id:"DL-sdlc-02", type:"order", q:"按应急响应（PDCERF）流程排列（↑↓ 调整）：", steps:["准备 Preparation","检测 Detection","抑制 Containment","根除 Eradication","恢复 Recovery","跟踪总结 Follow-up"], shuffled:["检测 Detection","准备 Preparation","根除 Eradication","抑制 Containment","跟踪总结 Follow-up","恢复 Recovery"], answerView:"准备→检测→抑制→根除→恢复→跟踪", analysis:"六阶段记忆：P-D-C-E-R-F。", source:"来源：教材17.5 应急响应与取证" },
      { id:"DL-sdlc-03", type:"fill", q:"补全：我国要求网络安全设施与信息化项目“同步规划、同步建设、＿＿＿”。", answer:"同步运行", alts:["同步运行","同步投入使用"], answerView:"同步规划、同步建设、同步运行（三同步）", analysis:"源自《网络安全法》与等保要求。", source:"来源：《网络安全法》第三十三条" }
    ]
  }
};
