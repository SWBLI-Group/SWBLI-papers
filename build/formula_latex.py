# -*- coding: utf-8 -*-
"""LaTeX source for each paper formula.

The build renders these strings to MathML at build time, so the site stays
fully offline (no MathJax/KaTeX CDN needed).  Each list item is one display
line; Chinese qualifiers live inside \text{...}.

The plain-text ``expr`` in content_*.json remains the fallback and is still
used by search / data consumers.
"""

FORMULA_LATEX = {
    1277: [
        r"q_{\mathrm{diff}}/q_{\mathrm{cond}} = \left( Pr/Sc \right)^{2/3} \approx 1.30",
    ],
    764: [
        r"M_\infty \theta_i \propto \chi^{0.5}",
    ],
    1316: [
        r"\left( M_\infty \theta_i \right)^2 \propto \chi",
    ],
    1256: [
        r"\frac{d^2 M_e}{dx^2} - \frac{M_e - M_\infty}{L_A^2} = 0",
    ],
    1056: [
        r"\frac{p_p - p_e}{q_e} = 1.47\, C_{f,e}^{0.5}\left(M_e^2 - 1\right)^{-1/4}",
    ],
    768: [
        r"M_\infty \delta_{\mathrm{incip}} = 1.3\,\chi^{0.5}",
        r"\chi = \frac{M_\infty^3\sqrt{C}}{\sqrt{Re_x}}",
    ],
    789: [
        r"\Delta t \le \left( \frac{|u|}{\Delta x} + \frac{|v|}{\Delta y} + c\sqrt{\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}} \right)^{-1}",
    ],
    1291: [
        r"\frac{dp}{dx} \sim R^{1/8},\qquad \Delta x \sim R^{-3/8}",
        r"p(x) = p_\infty - k(-x)^{1/2} + O(k^2),\qquad x<0",
    ],
    476: [
        r"St_{pk}^{(1)} = f\left(P_3/P_1,\ Re_L,\ Pr,\ H_e,\ T_w/T_e\right)",
        r"St_{pk}^{(3)} \approx 2.2\,St^{*}_{\mathrm{lam},(3)}\quad\text{（层流/层流）}",
        r"St_{pk}^{(3)} \approx 2.8\,St^{*}_{\mathrm{turb},(3)}\quad\text{（层流/湍流）}",
        r"St_{pk}^{(3)} \approx 2.5\,St^{*}_{\mathrm{trans},(3)}\quad\text{（层流/转捩）}",
    ],
    1202: [
        r"M_\infty \theta_i = f(\chi_L, S_w)",
    ],
    1166: [
        r"\lambda = U_w/U_\infty",
        r"\lambda < 0.3541:\quad \text{存在常规边界层解}",
        r"\lambda \ge 0.3541:\quad \text{需在 } x_s \text{ 附近引入 } O(R^{-1/4}) \text{ 无粘碰撞区}",
        r"x_s=0\ (0\le\lambda\le1),\qquad x_s<0\ (\lambda>1)",
    ],
    1069: [
        r"u(x_s,y_s)=0,\qquad \frac{\partial u}{\partial y}(x_s,y_s)=0",
        r"u(x,0)=u_w",
    ],
    475: [
        r"\frac{\Delta p_{i.s.}}{q} \propto \sqrt{c_f}",
    ],
    473: [
        r"\frac{q_{pk}}{q_{ref}} \approx a + B \left(\frac{p_{pk}}{p_{ref}}\right)^{1-n}\left(\frac{L_{pk}}{x_{pk}}\right)^n",
        r"\text{层流: }(a,B,n)=(0,1,0.5)",
        r"\text{湍流: }(0,1,0.2)",
        r"\text{湍流峰值/层流参考: }(0.3,0.072,0.2)",
    ],
    1350: [
        r"\nu_t = \frac{a_1 k}{\max\left(a_1\omega,\ \Omega F_2\right)}",
        r"F_2 = \tanh\left(\mathrm{arg}_2^2\right),\qquad \mathrm{arg}_2=\max\left(\frac{2\sqrt{k}}{0.09\omega y},\ \frac{500\nu}{y^2\omega}\right)",
        r"F_1=1\ \text{（近壁）};\qquad F_1=0\ \text{（外层）}",
        r"F_1\ \text{用于混合 } k\text{-}\omega \text{ 与 } k\text{-}\varepsilon \text{ 常数}",
    ],
    472: [
        r"\frac{q_{pk}}{q_{ref}} \approx a + B \left(\frac{p_{pk}}{p_{ref}}\right)^{1-n}\left(\frac{L_{pk}}{x_{pk}}\right)^n",
        r"L_{pk}\sim \text{Bushnell–Weinstein 再附边界层增长长度}",
    ],
    770: [
        r"p_{i.s.}=1.03,\qquad \theta_{i.s.}=1.52\,p_{i.s.}",
    ],
    478: [
        r"C_{p,sep/pla} = K_{sep/pla}\left[\left(M_0^2-1\right)Re_{\infty x_0}\right]^{-1/4}",
        r"K_{sep}=0.91,\qquad K_{pla}=1.68",
        r"\text{弱壁温修正约乘 } \left(T_w/T_0\right)^{-1/16}",
    ],
    1162: [
        r"f'(0)=K_1 f''(0),\qquad K_1=\frac{2-\sigma}{\sigma}\,Kn_x\sqrt{Re_x}",
    ],
    1071: [
        r"x_s:\quad \lim_{T\to\infty}\frac{\int_{t_0-T}^{t_0}\tau_w(x_s,t)/\rho(x_s,0,t)^2\,dt}{\int_{t_0-T}^{t_0}1/\rho(x_s,0,t)^2\,dt}=0",
        r"\tau_w=\mu\frac{\partial u}{\partial y}",
        r"\text{（加权极限有界）}",
    ],
    1150: [
        r"\alpha=U_w/U_\infty",
        r"0<\alpha<0.3541:\quad \text{存在两个解}",
        r"\alpha\ge0.3541:\quad \text{无物理解}",
    ],
    1172: [
        r"y \to y+y_0(x),\qquad \tilde{\psi}(x,y)=\psi\left[x,y+y_0(x)\right]",
        r"\tilde U_w(x)=u\left[x,y_0(x)\right],\qquad \tilde V_w(x)=v\left[x,y_0(x)\right]-y_0'(x)u\left[x,y_0(x)\right]",
    ],
    914: [
        r"R_{cc}=\frac{Re\,Pr(\gamma-1)\rho v\,(\partial T/\partial r)}{\partial\left(k\,\partial T/\partial r\right)/\partial r}=1.0",
        r"\frac{\partial v}{\partial r}=0,\qquad \frac{\partial p}{\partial r}=0,\qquad \frac{\partial}{\partial r}\left(k\frac{\partial T}{\partial r}\right)=0",
    ],
    1089: [
        r"V_w=O(Re^{-1/8}):\quad \text{三重台方程，壁面以 } V_w=-V_{sh} \text{ 运动}",
        r"1\gg V_w\gg Re^{-1/8}:\quad \text{匹配渐近展开，分离由局部解奇异性确定}",
    ],
    1086: [
        r"\frac{\partial p}{\partial x}=-A''(x)",
        r"\text{分离点取 } -A''(x) \text{ 的局部正峰（}A(x)\text{ 为下层位移函数）}",
    ],
    915: [
        r"L_{pk}=\sigma\kappa\delta_0,\qquad \kappa=\frac{2}{\tan\varphi},\qquad \delta_0=\frac{x_s}{\sqrt{Re_{x_s}}}",
        r"\frac{St_{pk}}{St_{ref}}=\left(\frac{p_{pk}}{p_{ref}}\right)^{1/2}\left(\frac{L_{pk}}{x_{ref}}\right)^{1/2}",
    ],
    461: [
        r"L_{int}/\delta \sim F(M_\infty,\ Re_\theta,\ p_3/p_1)",
        r"p_3/p_1 > C(M_\infty,\theta)\quad\text{（分离判据）}",
    ],
    1200: [
        r"M_1\theta_{is}=80\sqrt{\chi_L},\qquad \chi_L=\frac{M_1^3\sqrt{C}}{\sqrt{Re_L}}",
        r"C=\frac{\mu_w}{\mu_1}\frac{T_1}{T_w}",
    ],
    375: [
        r"\frac{q_{s,ne}}{q_{s,e}}=1-\frac{\tilde{\alpha}_\delta}{\tilde{\mu}}",
        r"\frac{\alpha_\delta}{\alpha_e}=\frac{Da_d^{0.8}}{Da_d^{0.8}+1/19}",
        r"\varphi=1-\frac{\alpha_{rec}}{\alpha_\delta}=\frac{1}{1+Da_r}",
        r"W_r=2^J M_\infty^2\frac{\omega}{Re_\infty}",
    ],
    1324: [
        r"L/\delta=C\left(T_w/T_r\right)^{0.85}",
        r"C\approx2.9\ \text{（}24^\circ\text{ 拐角，}M_\infty=2.9\text{）}",
        r"20^\circ\text{ 拐角: }C\approx1.28",
    ],
    1073: [
        r"x_s(t_0):\quad \mathrm{FTLE}(x_s,t_0,T)=0,\qquad T\ \text{取一个周期}",
        r"\text{沿壁面的带符号 }\mathrm{FTLE}\text{ 在该点由正变负}",
    ],
    459: [
        r"L_R^*=L_R/h\propto\dot m_R^*",
        r"\Gamma_V^*\propto\left(\dot m_R^*\right)^2",
        r"C_{p,b}\approx C_{p,V}\propto\dot m_R^*,\qquad \dot m_R^*=\frac{\dot m_R}{\rho U_\infty h}",
    ],
    917: [
        r"C_Q=\int\frac{C_h}{\cos\theta}\,d\bar x",
        r"C_D=\int C_f\,d\bar x+\int C_p\tan\theta\,d\bar x",
        r"\text{附着: }C_Q/C_D=f(h/\delta,Ma_\infty,Re_\lambda)",
        r"\text{分离: }C_Q/C_D=g(\bar x)",
    ],
    1091: [
        r"V_{sh}=O(Re^{-1/8}):\quad \text{三重台方程，MRS 条件 }u=\partial u/\partial y=0",
        r"1\gg V_{sh}\gg Re^{-1/8}:\quad \hat P=\frac{8\pi^2/\chi^2}{\left(\hat X-\hat X_0\right)^2}\quad\left(\hat X\to\hat X_0\right)",
    ],
    742: [
        r"L/\delta=F(p_3/p_1,\ Re_\theta)",
        r"\text{以真实激波马赫数 }M_s\text{ 折算}",
    ],
    387: [
        r"\frac{q_w}{q_{w,ca}}=1-\tilde\eta_v\chi(Da_{v,a})",
        r"\tilde\eta_v=\frac{\beta_{Pr}^{2/3}\eta_v}{1+\beta_{Pr}^{2/3}\eta_v}",
        r"\chi=\frac{1}{1+Da_{v,a}}",
        r"Da_{v,a}=A\frac{Re_{x,e}^{1/2}}{Ma_e}\left(\frac{T_{tr,e}}{T_w}\right)^{1/2}\sigma_v,\qquad A\approx0.9",
    ],
    499: [
        r"q_w=\Theta_0'(0)\frac{k_w}{\delta_0}\frac{\rho_w}{\rho_e}(T_{aw}-T_w)",
        r"\delta_0=\sqrt{\frac{\mu_e}{\rho_e\beta}}",
        r"\psi_e=\beta xy+\frac12\zeta y^2,\qquad \tan\theta=\frac{2\beta}{\zeta}",
        r"St_e=\Theta_0'(0)\frac{C_w}{Pr}\sqrt{\frac{H_\beta}{M_e}}\sqrt{\frac{\bar T_{aw}-\bar T_w}{\gamma-1}}",
    ],
    932: [
        r"K_s^2=\frac{P_p^2 Ma_1^3 c_{f,o}}{(\gamma+1)\left(P_p Ma_1^3 c_{f,o}\right)^{1/2}+4}",
        r"\theta_s\approx\frac{0.756\,\theta_w^{3/8}}{Ma_1^{1/16}Re^{3/32}}",
        r"p_{pk}/p_1\approx n Ma_1^2\theta_r^2,\qquad \theta_r=\theta_w-\theta_s",
    ],
    380: [
        r"q_w\approx-\Theta_0'(0)\frac{k_w}{\delta_0}\frac{\rho_w}{\rho_e}(T_{aw}-T_w)",
        r"\delta_0=\sqrt{\frac{\mu_e}{\rho_e a}}",
        r"\psi=\delta_0^2\left[\xi f(\eta)+g(\eta)\right]",
        r"T-T_w=(T_{aw}-T_e)\left(\Theta_0+\Theta_1\xi+\Theta_2\xi^2\right)",
    ],
    793: [
        r"\beta_{crit}=\beta_{crit}(M_\infty,Re)",
        r"\beta>\beta_{crit}:\quad \text{出现定常全局不稳定}",
        r"M_\infty=2.15,\ Re=1\times10^5:\quad \beta_{crit}\approx31.8^\circ",
    ],
    503: [
        r"L/\delta=L_{qs}(p_3/p_1,\ Re_\theta,\ T_w/T_r)\quad\text{（区间 I）}",
        r"L/\delta\to0\quad\text{当 }M_s\to M_{s,max}\text{（区间 II 末端）}",
    ],
    928: [
        r"q_w=\left[1+\beta_{Pr}^{2/3}\frac{e_{v,e}-e_{v,w}}{h_{tr,aw}-h_{tr,w}}\right]q_{tr}",
        r"\beta_{Pr}=Pr_{tr}/Pr_v=0.864",
    ],
    993: [
        r"L/L_{ref}\sim F(M_\infty,\ Re,\ T_w/T_0,\ \text{构型因子})",
        r"L_{ref}\ \text{取边界层厚度或构型特征长度}",
        r"\text{二维高/低 }Re\text{ 分段}",
    ],
    884: [
        r"\theta_{crit,1\to2}=f(M_\infty,\ Re_\delta,\ \text{边界层状态})",
        r"\theta_{crit,2\to3}=g(M_\infty,\ Re_\delta,\ \text{边界层状态})",
    ],
    1255: [
        r"Nu_x=Re_x^{1/2}\left[-\theta'(0;Pr)\right]",
        r"\theta'(0;Pr)\ \text{由精确边界层解沿法向的积分确定}",
        r"\text{大 }Pr\text{ 时由 Laplace 方法给出渐近展开并与精确式拼接}",
    ],
    339: [
        r"\frac{q_c}{q_{tr}}=Le^{-0.6}\frac{\alpha_1}{\tilde\mu-\alpha_1}\frac{Da_c}{1+Da_c}",
        r"Da_c=\frac{Sc^{2/3}\sqrt{C^*}}{0.332\sqrt{2\pi\gamma}}\frac{Re_{x,e}^{1/2}}{Ma_e}\left(\frac{T_{tr,e}}{T_w}\right)^{1/2}\gamma_{cat}",
        r"\tilde\mu=E_\infty/E_d",
    ],
    902: [
        r"L(t)/L_{ref}=F(\tau;\ p_3/p_1)",
        r"h(t)/L_{ref}=G(\tau;\ p_3/p_1)",
        r"\tau\ \text{为无量纲时间}",
    ],
    1094: [
        r"\alpha=\alpha_c:\quad u(x_s,y_s)=0,\qquad \frac{\partial u}{\partial y}(x_s,y_s)=0",
        r"\text{其后 }\delta(x)\text{ 突增并形成闭合流线回流区}",
    ],
    384: [
        r"p_{sep}/p_\infty=F(\chi,\bar V)",
        r"\chi\ \text{为高超声速相似参数},\qquad \bar V\ \text{为湍流黏性干扰参数}",
        r"\text{等价自变量: }M_\infty,\ Re,\ T_w/T_0",
    ],
    1039: [
        r"L/\delta=f(\Pi),\qquad \Pi=\frac{S_d-S_r}{S_r}",
        r"S_d\ \text{为入射激波扰动强度},\qquad S_r\ \text{为边界层剪切抵抗强度}",
    ],
    1303: [
        r"L/\delta=L_{\mathrm{Katzer}}(M_\infty,Re)\,\Phi(T_w/T_0)",
        r"\Phi\ \text{为壁温修正函数}",
        r"M_\infty=1.6\text{–}15,\qquad T_w/T_0=0.2\text{–}1",
    ],
    934: [
        r"\frac{q_c}{q_{tr}}=Le^{-0.6}\frac{\alpha_1}{\tilde\mu-\alpha_1}\frac{Da_c}{1+Da_c}",
        r"L_c=L+L_{CR},\qquad Re_{L_c,e}\ \text{代入}",
        r"L_c=L+\frac{\sin\theta_s}{\sin(\theta_w-\theta_s)}(L-x_u)",
        r"\theta_s\approx\frac{0.755\,\theta_w^{3/8}}{Ma_\infty^{1/16}Re^{3/32}}\,L",
    ],
    2001: [
        r"U'(t+\Delta\tau)=G_{\Delta\tau}U'(t),\qquad G_{\Delta\tau}=e^{A\Delta\tau}",
        r"\omega_k=\frac{i}{\Delta\tau}\ln\mu_k",
    ],
    2004: [
        r"f_k\pm f_l=f_m",
        r"\text{显著耦合：}\left\|\lambda_1(St_k,St_l)\right\|\text{ 的局部极大}",
    ],
    2005: [
        r"\tilde Q(x,y,z,t)=\hat Q(x,z)\,e^{i(\beta y-\Omega t)}+\mathrm{c.c.}",
        r"\Omega=\Omega_r+i\Omega_i,\qquad \beta=2\pi/L_y",
    ],
    2006: [
        r"|KE|^2=\sqrt{(U-U_b)^2+V^2+(W-W_b)^2}",
    ],
    2007: [
        r"\sigma(St_L)=\frac{\sigma_0}{\sqrt{1+\left(St_L/(\omega_i^{(S1)}/2\pi)\right)^2}}",
    ],
    2008: [
        r"G(t)=\frac{\|q(t)\|_E^2}{\|q(0)\|_E^2},\qquad q(t)=e^{At}q(0)",
    ],
    2009: [
        r"A\hat q=-i\omega\hat q",
        r"q'(x,y,z,t)=\hat q(x,y)\,e^{i(\beta z-\omega t)}",
    ],
    2010: [
        r"\bar u_s\,\partial_s\omega'_s\approx\frac{\partial_n\bar\rho}{\bar\rho^2}\,i\beta p'-\partial_n\bar u_s\,\partial_s w'-\frac{2\bar u_s}{R}\,i\beta u'_s",
    ],
    2011: [
        r"J(q)=\left[\int(\tau_w-\tau_{w,0})\,dx\right]^2,\qquad \|f\|_F^2=A^2",
        r"2\lambda f=Q_F^{-1}P^*M^*\tilde q",
    ],
    2012: [
        r"I_{cw}<I_b<I_{sb}\ \Rightarrow\ \text{双解共存}",
        r"I_b>I_{sb}\ \Rightarrow\ \text{必附着},\qquad I_b<I_{cw}\ \Rightarrow\ \text{必分离}",
    ],
    2014: [
        r"s(t)=s_T(t)+s_R(t)",
        r"s_T\sim\mathcal{N}(\mu_T,\sigma_T^2),\qquad s_R\sim\mathcal{N}(0,\sigma_R^2)",
    ],
    2015: [
        r"\mathrm{LIM2}(k,\tau)=\frac{|G_\Psi(k,\tau)|^4}{\langle|G_\Psi(k,\tau)|^2\rangle_\tau^2}",
    ],
    2035: [
        r"St_{L_{sep}}=\frac{f\,L_{sep}}{U_\infty}",
    ],
    2038: [
        r"F=1+9\,II+27\,III",
    ],
    2039: [
        r"L=\frac{26.91\,AOA-119}{AOA-3.158}",
    ],
    2041: [
        r"L/\delta^*=F\!\left(M_\infty,Re,T_w/T_0,\theta,p_2/p_1,h_0\right)",
    ],
    2042: [
        r"L/\delta^*=A\chi^m,\qquad \chi=\chi_0\left(T_w/T_0\right)^a",
    ],
    2044: [
        r"q(x,t)=\bar q(x)+\varepsilon\hat q(x)e^{-i\omega t}",
        r"A\hat q=-i\omega\hat q",
    ],
    2045: [
        r"\dot\rho=(\alpha_1+\alpha_2\rho^2)\rho,\qquad \dot\theta=\beta_1+\beta_2\rho^2",
    ],
    2046: [
        r"G_T=\frac{\rho_\infty u_\infty}{\mu_{t,peak}}\,\theta\sqrt{\frac{\theta}{R}},\qquad G_{T,c}\approx0.45",
    ],
    2047: [
        r"q_w/q_{ref}=(Re/Re_{ref})^n\left(T_w/T_0\right)^m",
    ],
    2048: [
        r"C_f=C_{f,lam}+C_{f,turb}+C_{f,\text{其他}}",
    ],
    2049: [
        r"p_{\mathrm{dB}} = 20\log_{10}\left(\frac{p_{\mathrm{rms}}}{2\times10^{-5}\ \mathrm{Pa}}\right)",
    ],
    346: [
        r"\bar{P}=\frac{p_d-p_1}{p_1}-\bar{P}_{\mathrm{anti}}",
        r"\frac{L_s}{x_s}=\alpha\bar{P}\quad\Longrightarrow\quad L_s=\frac{x_s\,\alpha\bar{P}}{1+\alpha\bar{P}}",
    ],
    1480: [
        r"L^{*}=\frac{L}{\delta^{*}G_3},\qquad G_3=\frac{\sin\beta\,\sin\varphi}{\sin(\beta-\varphi)}",
        r"S_r^{*}=\frac{p_3/p_1}{\left(p/p_1\right)_{\mathrm{sep}}}\approx\frac{p_3}{p_2}",
    ],
    1505: [
        r"L^{*}=\frac{L}{\delta^{*}G_3},\qquad G_3=\frac{\sin\beta\,\sin\varphi}{\sin(\beta-\varphi)}",
        r"S_e^{*,\mathrm{mod}}\approx\frac{\Delta p}{\Delta p_{\mathrm{sep}}}",
    ],
    1511: [
        r"L_0=0.39\,C_{x0},\qquad D_0=0.50\,C_{x0}^{3/2}",
        r"c_p=-2.56\,Re^{-1/2}\sqrt{C_{x0}},\qquad L=Re\,L_0,\quad D=Re^{1/2}D_0",
    ],
    1540: [
        r"\sigma_{tp}=\frac{p_{t2}}{p_{t1}},\qquad \eta_B=\frac{h(T_{2,\mathrm{isen}})-h(T_1)}{h(T_2)-h(T_1)}",
        r"T_{2,\mathrm{isen}}=T_1\left(\frac{p_2}{p_1}\right)^{(\gamma-1)/\gamma}",
    ],
    1563: [
        r"St=\frac{f\,L_{\mathrm{sep}}}{U_\infty},\qquad 0.02<St<0.05",
    ],
}
