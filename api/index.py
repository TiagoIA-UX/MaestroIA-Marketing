from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import os
import secrets
import httpx

app = FastAPI(
    title="MaestroIA API",
    description="Orquestrador de Agentes de IA para Marketing Digital",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===========================
# OAUTH CONFIGURATION
# ===========================

OAUTH_REDIRECT_BASE_URL = os.getenv("OAUTH_REDIRECT_BASE_URL", "https://maestroia.vercel.app")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GITHUB_OAUTH_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID")
GITHUB_OAUTH_CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")

# ===========================
# OAUTH ROUTES - GOOGLE
# ===========================

@app.get("/auth/google/start")
def google_oauth_start():
    """Inicia fluxo de autenticação com Google"""
    if not GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth não configurado")
    
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{OAUTH_REDIRECT_BASE_URL}/auth/google/callback"
    
    params = f"client_id={GOOGLE_OAUTH_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile&access_type=offline&prompt=consent&state={state}"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    
    return RedirectResponse(url=auth_url)


@app.get("/auth/google/callback")
async def google_oauth_callback(code: str = Query(None), error: str = Query(None)):
    """Callback do Google OAuth"""
    if error:
        return RedirectResponse(url=f"/app?error={error}")
    
    if not code:
        return RedirectResponse(url="/app?error=no_code")
    
    redirect_uri = f"{OAUTH_REDIRECT_BASE_URL}/auth/google/callback"
    
    async with httpx.AsyncClient() as client:
        # Trocar código por token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }
        )
        
        if token_response.status_code != 200:
            return RedirectResponse(url="/app?error=token_failed")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        # Obter informações do usuário
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if userinfo_response.status_code != 200:
            return RedirectResponse(url="/app?error=userinfo_failed")
        
        user_info = userinfo_response.json()
        
        # Para demo: redireciona para dashboard com nome do usuário
        name = user_info.get("name", "Usuário")
        email = user_info.get("email", "")
        picture = user_info.get("picture", "")
        
        # Redireciona com dados do usuário (em produção real, criaria sessão/JWT)
        return RedirectResponse(url=f"/app?login=success&provider=google&name={name}&email={email}&picture={picture}")


# ===========================
# OAUTH ROUTES - GITHUB
# ===========================

@app.get("/auth/github/start")
def github_oauth_start():
    """Inicia fluxo de autenticação com GitHub"""
    if not GITHUB_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GitHub OAuth não configurado")
    
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{OAUTH_REDIRECT_BASE_URL}/auth/github/callback"
    
    params = f"client_id={GITHUB_OAUTH_CLIENT_ID}&redirect_uri={redirect_uri}&scope=user:email%20read:user&state={state}"
    auth_url = f"https://github.com/login/oauth/authorize?{params}"
    
    return RedirectResponse(url=auth_url)


@app.get("/auth/github/callback")
async def github_oauth_callback(code: str = Query(None), error: str = Query(None)):
    """Callback do GitHub OAuth"""
    if error:
        return RedirectResponse(url=f"/app?error={error}")
    
    if not code:
        return RedirectResponse(url="/app?error=no_code")
    
    redirect_uri = f"{OAUTH_REDIRECT_BASE_URL}/auth/github/callback"
    
    async with httpx.AsyncClient() as client:
        # Trocar código por token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_OAUTH_CLIENT_ID,
                "client_secret": GITHUB_OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            return RedirectResponse(url="/app?error=token_failed")
        
        tokens = token_response.json()
        
        if "error" in tokens:
            return RedirectResponse(url=f"/app?error={tokens.get('error')}")
        
        access_token = tokens.get("access_token")
        
        # Obter informações do usuário
        userinfo_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )
        
        if userinfo_response.status_code != 200:
            return RedirectResponse(url="/app?error=userinfo_failed")
        
        user_info = userinfo_response.json()
        
        # Se o email não estiver público, buscar emails
        email = user_info.get("email")
        if not email:
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                for e in emails:
                    if e.get("primary"):
                        email = e.get("email")
                        break
        
        name = user_info.get("name") or user_info.get("login", "Usuário")
        picture = user_info.get("avatar_url", "")
        
        return RedirectResponse(url=f"/app?login=success&provider=github&name={name}&email={email}&picture={picture}")


# ===========================
# OAUTH STATUS
# ===========================

@app.get("/auth/status")
def oauth_status():
    """Retorna status dos providers OAuth"""
    return JSONResponse({
        "google": {
            "configured": bool(GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET),
            "start_url": "/auth/google/start"
        },
        "github": {
            "configured": bool(GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET),
            "start_url": "/auth/github/start"
        }
    })


@app.get("/")
def root():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>MaestroIA — Orquestrador de Agentes de IA para Marketing</title>
  <meta name="description" content="Automatize campanhas de marketing com inteligência artificial. Agentes especializados trabalhando 24/7 para escalar seu negócio."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    :root{
      --bg:#030712;--bg2:#0f172a;--bg3:#1e293b;
      --text:#f1f5f9;--text2:#94a3b8;--text3:#64748b;
      --primary:#6366f1;--primary-hover:#818cf8;--primary-glow:rgba(99,102,241,.35);
      --accent:#22d3ee;--success:#10b981;--warning:#f59e0b;
      --glass:rgba(15,23,42,.7);--border:rgba(148,163,184,.12);
      --gradient:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#d946ef 100%);
    }
    html{scroll-behavior:smooth}
    body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}
    
    /* Animated Background */
    .bg-grid{position:fixed;inset:0;background-image:radial-gradient(rgba(99,102,241,.1) 1px,transparent 1px);background-size:50px 50px;pointer-events:none;z-index:-1}
    .bg-glow{position:fixed;width:600px;height:600px;background:radial-gradient(circle,var(--primary-glow) 0%,transparent 70%);border-radius:50%;filter:blur(80px);pointer-events:none;z-index:-1}
    .bg-glow.g1{top:-200px;left:-100px}
    .bg-glow.g2{bottom:-300px;right:-200px;background:radial-gradient(circle,rgba(139,92,246,.25) 0%,transparent 70%)}
    
    /* Layout */
    .container{max-width:1200px;margin:0 auto;padding:0 24px}
    section{padding:100px 0}
    
    /* Typography */
    h1,h2,h3,h4{font-weight:700;line-height:1.2}
    h1{font-size:clamp(2.5rem,6vw,4.5rem);letter-spacing:-0.03em}
    h2{font-size:clamp(2rem,4vw,3rem);letter-spacing:-0.02em}
    h3{font-size:1.5rem}
    .gradient-text{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .text-muted{color:var(--text2)}
    .text-sm{font-size:.875rem}
    .text-center{text-align:center}
    
    /* Buttons */
    .btn{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;border-radius:12px;font-weight:600;font-size:1rem;text-decoration:none;transition:all .3s ease;cursor:pointer;border:none}
    .btn-primary{background:var(--gradient);color:#fff;box-shadow:0 4px 20px var(--primary-glow)}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px var(--primary-glow)}
    .btn-secondary{background:var(--glass);color:var(--text);border:1px solid var(--border);backdrop-filter:blur(10px)}
    .btn-secondary:hover{background:var(--bg3);border-color:var(--primary)}
    .btn-ghost{background:transparent;color:var(--text2);padding:8px 16px}
    .btn-ghost:hover{color:var(--text)}
    
    /* Header */
    header{position:fixed;top:0;left:0;right:0;z-index:100;padding:16px 0;transition:all .3s ease}
    header.scrolled{background:var(--glass);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}
    .header-inner{display:flex;align-items:center;justify-content:space-between}
    .logo{display:flex;align-items:center;gap:10px;font-size:1.5rem;font-weight:800;text-decoration:none;color:var(--text)}
    .logo svg{width:40px;height:40px}
    nav{display:flex;align-items:center;gap:8px}
    nav a{color:var(--text2);text-decoration:none;padding:8px 16px;border-radius:8px;font-size:.9rem;transition:all .2s}
    nav a:hover{color:var(--text);background:var(--bg3)}
    .nav-cta{margin-left:16px}
    .mobile-menu{display:none;background:none;border:none;color:var(--text);cursor:pointer}
    
    /* Hero */
    .hero{min-height:100vh;display:flex;align-items:center;padding-top:100px}
    .hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}
    .hero-badge{display:inline-flex;align-items:center;gap:8px;background:var(--glass);border:1px solid var(--border);padding:8px 16px;border-radius:50px;font-size:.85rem;color:var(--text2);margin-bottom:24px}
    .hero-badge span{background:var(--success);color:#000;padding:2px 8px;border-radius:20px;font-size:.75rem;font-weight:600}
    .hero h1{margin-bottom:24px}
    .hero p{font-size:1.25rem;color:var(--text2);margin-bottom:32px;max-width:540px}
    .hero-buttons{display:flex;gap:16px;flex-wrap:wrap}
    .hero-stats{display:flex;gap:40px;margin-top:48px;padding-top:32px;border-top:1px solid var(--border)}
    .stat{text-align:left}
    .stat-value{font-size:2rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .stat-label{font-size:.85rem;color:var(--text3)}
    .hero-image{position:relative}
    .hero-image img{width:100%;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
    .hero-image::before{content:'';position:absolute;inset:-2px;background:var(--gradient);border-radius:22px;z-index:-1;opacity:.5}
    .floating-card{position:absolute;background:var(--glass);backdrop-filter:blur(10px);border:1px solid var(--border);border-radius:12px;padding:16px;animation:float 3s ease-in-out infinite}
    .floating-card.fc1{top:20%;left:-40px;animation-delay:0s}
    .floating-card.fc2{bottom:20%;right:-40px;animation-delay:1.5s}
    @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
    
    /* Logos */
    .logos{padding:60px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
    .logos p{text-align:center;color:var(--text3);font-size:.9rem;margin-bottom:32px}
    .logos-grid{display:flex;justify-content:center;align-items:center;gap:48px;flex-wrap:wrap;opacity:.6}
    .logos-grid img{height:32px;filter:grayscale(1) brightness(2)}
    
    /* Features */
    .features-header{text-align:center;max-width:700px;margin:0 auto 60px}
    .features-header p{color:var(--text2);font-size:1.1rem;margin-top:16px}
    .features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .feature-card{background:var(--glass);border:1px solid var(--border);border-radius:20px;padding:32px;transition:all .3s ease;position:relative;overflow:hidden}
    .feature-card:hover{transform:translateY(-5px);border-color:var(--primary);box-shadow:0 20px 40px rgba(99,102,241,.1)}
    .feature-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--gradient);opacity:0;transition:opacity .3s}
    .feature-card:hover::before{opacity:1}
    .feature-icon{width:56px;height:56px;background:linear-gradient(135deg,var(--primary) 0%,#8b5cf6 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;margin-bottom:20px}
    .feature-icon svg{width:28px;height:28px;color:#fff}
    .feature-card h3{margin-bottom:12px}
    .feature-card p{color:var(--text2);font-size:.95rem}
    .feature-image{margin-top:20px;border-radius:12px;overflow:hidden}
    .feature-image img{width:100%;height:180px;object-fit:cover;transition:transform .3s}
    .feature-card:hover .feature-image img{transform:scale(1.05)}
    
    /* How it Works */
    .how-it-works{background:var(--bg2)}
    .steps{display:grid;grid-template-columns:repeat(4,1fr);gap:32px;margin-top:60px;position:relative}
    .steps::before{content:'';position:absolute;top:40px;left:10%;right:10%;height:2px;background:linear-gradient(90deg,transparent,var(--primary),var(--accent),var(--primary),transparent)}
    .step{text-align:center;position:relative}
    .step-number{width:80px;height:80px;background:var(--gradient);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;margin:0 auto 24px;position:relative;z-index:1}
    .step h3{margin-bottom:12px}
    .step p{color:var(--text2);font-size:.9rem}
    
    /* Showcase */
    .showcase-grid{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}
    .showcase-content h2{margin-bottom:20px}
    .showcase-content p{color:var(--text2);margin-bottom:32px}
    .showcase-list{list-style:none;margin-bottom:32px}
    .showcase-list li{display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;color:var(--text2)}
    .showcase-list svg{width:24px;height:24px;color:var(--success);flex-shrink:0;margin-top:2px}
    .showcase-image{position:relative}
    .showcase-image img{width:100%;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.4)}
    
    /* Pricing */
    .pricing{background:var(--bg2)}
    .pricing-header{text-align:center;max-width:600px;margin:0 auto 60px}
    .pricing-toggle{display:flex;justify-content:center;gap:16px;align-items:center;margin-top:24px}
    .pricing-toggle span{color:var(--text2);font-size:.9rem}
    .pricing-toggle span.active{color:var(--text)}
    .toggle{width:60px;height:32px;background:var(--bg3);border-radius:20px;position:relative;cursor:pointer;border:1px solid var(--border)}
    .toggle::after{content:'';position:absolute;top:4px;left:4px;width:24px;height:24px;background:var(--primary);border-radius:50%;transition:transform .3s}
    .toggle.active::after{transform:translateX(26px)}
    .pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .pricing-card{background:var(--glass);border:1px solid var(--border);border-radius:24px;padding:40px;position:relative;transition:all .3s}
    .pricing-card.featured{border-color:var(--primary);transform:scale(1.05)}
    .pricing-card.featured::before{content:'MAIS POPULAR';position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--gradient);padding:6px 20px;border-radius:20px;font-size:.75rem;font-weight:600}
    .pricing-card:hover{border-color:var(--primary)}
    .pricing-name{font-size:1.25rem;font-weight:600;margin-bottom:8px}
    .pricing-desc{color:var(--text2);font-size:.9rem;margin-bottom:24px}
    .pricing-price{font-size:3rem;font-weight:800;margin-bottom:8px}
    .pricing-price span{font-size:1rem;color:var(--text2);font-weight:400}
    .pricing-features{list-style:none;margin:32px 0;padding-top:32px;border-top:1px solid var(--border)}
    .pricing-features li{display:flex;align-items:center;gap:12px;margin-bottom:16px;font-size:.95rem;color:var(--text2)}
    .pricing-features svg{width:20px;height:20px;color:var(--success)}
    .pricing-card .btn{width:100%;justify-content:center}
    
    /* Testimonials */
    .testimonials-header{text-align:center;max-width:600px;margin:0 auto 60px}
    .testimonials-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .testimonial-card{background:var(--glass);border:1px solid var(--border);border-radius:20px;padding:32px;transition:all .3s}
    .testimonial-card:hover{border-color:var(--primary)}
    .testimonial-stars{color:var(--warning);margin-bottom:16px;letter-spacing:2px}
    .testimonial-text{color:var(--text2);font-size:.95rem;line-height:1.7;margin-bottom:24px}
    .testimonial-author{display:flex;align-items:center;gap:16px}
    .testimonial-avatar{width:48px;height:48px;border-radius:50%;object-fit:cover}
    .testimonial-info h4{font-size:.95rem;font-weight:600}
    .testimonial-info p{font-size:.85rem;color:var(--text3)}
    
    /* FAQ */
    .faq{background:var(--bg2)}
    .faq-header{text-align:center;max-width:600px;margin:0 auto 60px}
    .faq-grid{max-width:800px;margin:0 auto}
    .faq-item{border-bottom:1px solid var(--border);padding:24px 0}
    .faq-question{display:flex;justify-content:space-between;align-items:center;cursor:pointer;font-weight:600;font-size:1.1rem}
    .faq-question svg{width:24px;height:24px;color:var(--text2);transition:transform .3s}
    .faq-item.active .faq-question svg{transform:rotate(45deg)}
    .faq-answer{max-height:0;overflow:hidden;transition:all .3s ease;color:var(--text2);line-height:1.7}
    .faq-item.active .faq-answer{max-height:200px;padding-top:16px}
    
    /* CTA */
    .cta{text-align:center;padding:120px 0}
    .cta-box{background:var(--gradient);border-radius:32px;padding:80px;position:relative;overflow:hidden}
    .cta-box::before{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1639322537228-f710d846310a?w=1200&q=80');background-size:cover;opacity:.1}
    .cta-content{position:relative;z-index:1}
    .cta h2{margin-bottom:20px}
    .cta p{font-size:1.25rem;opacity:.9;margin-bottom:32px;max-width:600px;margin-left:auto;margin-right:auto}
    .cta-buttons{display:flex;justify-content:center;gap:16px}
    .cta .btn-primary{background:#fff;color:var(--primary)}
    .cta .btn-secondary{border-color:rgba(255,255,255,.3);color:#fff}
    
    /* Footer */
    footer{background:var(--bg);border-top:1px solid var(--border);padding:60px 0 30px}
    .footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:48px;margin-bottom:48px}
    .footer-brand p{color:var(--text2);margin-top:16px;font-size:.9rem;max-width:300px}
    .footer-social{display:flex;gap:12px;margin-top:20px}
    .footer-social a{width:40px;height:40px;background:var(--bg3);border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--text2);transition:all .2s}
    .footer-social a:hover{background:var(--primary);color:#fff}
    .footer-links h4{font-size:.9rem;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:20px}
    .footer-links a{display:block;color:var(--text2);text-decoration:none;font-size:.9rem;margin-bottom:12px;transition:color .2s}
    .footer-links a:hover{color:var(--text)}
    .footer-bottom{display:flex;justify-content:space-between;align-items:center;padding-top:30px;border-top:1px solid var(--border);color:var(--text3);font-size:.85rem}
    .footer-bottom a{color:var(--text2);text-decoration:none}
    
    /* Responsive */
    @media(max-width:1024px){
      .hero-grid,.showcase-grid{grid-template-columns:1fr;text-align:center}
      .hero-image{order:-1}
      .hero p{margin-left:auto;margin-right:auto}
      .hero-stats{justify-content:center}
      .steps{grid-template-columns:repeat(2,1fr)}
      .steps::before{display:none}
      .pricing-grid{grid-template-columns:1fr}
      .pricing-card.featured{transform:none}
    }
    @media(max-width:768px){
      section{padding:60px 0}
      .features-grid,.testimonials-grid{grid-template-columns:1fr}
      nav{display:none}
      .mobile-menu{display:block}
      .hero-buttons{justify-content:center}
      .footer-grid{grid-template-columns:1fr 1fr}
      .cta-box{padding:40px 24px}
      .floating-card{display:none}
    }
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow g1"></div>
  <div class="bg-glow g2"></div>

  <!-- Header -->
  <header id="header">
    <div class="container header-inner">
      <a href="#" class="logo">
        <svg viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="url(#lg)" stroke-width="3"/><path d="M14 20l4 4 8-8" stroke="url(#lg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="lg" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#d946ef"/></linearGradient></defs></svg>
        MaestroIA
      </a>
      <nav>
        <a href="#features">Recursos</a>
        <a href="#how">Como Funciona</a>
        <a href="#pricing">Preços</a>
        <a href="#faq">FAQ</a>
        <a href="/app" class="nav-cta btn btn-primary" style="padding:10px 20px">Acessar Plataforma</a>
      </nav>
      <button class="mobile-menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
      </button>
    </div>
  </header>

  <!-- Hero -->
  <section class="hero">
    <div class="container">
      <div class="hero-grid">
        <div class="hero-content">
          <div class="hero-badge">
            <span>NOVO</span>
            Orquestração de IA para Marketing
          </div>
          <h1>Automatize seu <span class="gradient-text">Marketing Digital</span> com Agentes de IA</h1>
          <p>6 agentes especializados trabalhando em conjunto para pesquisar, criar, otimizar e publicar suas campanhas. Resultados 10x mais rápidos com qualidade profissional.</p>
          <div class="hero-buttons">
            <a href="/app" class="btn btn-primary">
              Começar Gratuitamente
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </a>
            <a href="#how" class="btn btn-secondary">Ver Demonstração</a>
          </div>
          <div class="hero-stats">
            <div class="stat">
              <div class="stat-value">10x</div>
              <div class="stat-label">Mais Rápido</div>
            </div>
            <div class="stat">
              <div class="stat-value">85%</div>
              <div class="stat-label">Menos Custo</div>
            </div>
            <div class="stat">
              <div class="stat-value">24/7</div>
              <div class="stat-label">Operação</div>
            </div>
          </div>
        </div>
        <div class="hero-image">
          <img src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80" alt="Inteligência Artificial"/>
          <div class="floating-card fc1">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:40px;height:40px;background:linear-gradient(135deg,#22d3ee,#6366f1);border-radius:10px;display:flex;align-items:center;justify-content:center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
              </div>
              <div>
                <div style="font-weight:600;font-size:.9rem">Campanha Criada</div>
                <div style="color:var(--text3);font-size:.75rem">Agora mesmo</div>
              </div>
            </div>
          </div>
          <div class="floating-card fc2">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:40px;height:40px;background:linear-gradient(135deg,#10b981,#22d3ee);border-radius:10px;display:flex;align-items:center;justify-content:center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/></svg>
              </div>
              <div>
                <div style="font-weight:600;font-size:.9rem">+340% ROI</div>
                <div style="color:var(--text3);font-size:.75rem">Esta semana</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Logos -->
  <section class="logos">
    <div class="container">
      <p>Integrações com as principais plataformas</p>
      <div class="logos-grid">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Google_Ads_Logo.svg/512px-Google_Ads_Logo.svg.png" alt="Google Ads"/>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Meta_Inc._logo_%282023%29.svg/512px-Meta_Inc._logo_%282023%29.svg.png" alt="Meta"/>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/OpenAI_Logo.svg/512px-OpenAI_Logo.svg.png" alt="OpenAI"/>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Linkedin_icon.svg/256px-Linkedin_icon.svg.png" alt="LinkedIn"/>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Mercado_Pago_Logo.svg/512px-Mercado_Pago_Logo.svg.png" alt="Mercado Pago"/>
      </div>
    </div>
  </section>

  <!-- Features -->
  <section id="features">
    <div class="container">
      <div class="features-header">
        <h2>6 Agentes de IA <span class="gradient-text">Trabalhando por Você</span></h2>
        <p>Cada agente é especialista em uma etapa do funil de marketing, colaborando em tempo real para entregar resultados excepcionais.</p>
      </div>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          </div>
          <h3>Pesquisador</h3>
          <p>Analisa tendências, concorrência e comportamento do público para insights estratégicos.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&q=80" alt="Analytics Dashboard"/>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <h3>Estrategista</h3>
          <p>Define posicionamento, tom de voz e estratégias personalizadas para cada campanha.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80" alt="Strategy Planning"/>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>
          </div>
          <h3>Criador de Conteúdo</h3>
          <p>Produz textos, headlines e copies persuasivos otimizados para conversão.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=600&q=80" alt="Content Creation"/>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
          </div>
          <h3>Otimizador</h3>
          <p>Aplica SEO, ajusta campanhas em tempo real e maximiza performance.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=600&q=80" alt="Performance Optimization"/>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
          </div>
          <h3>Publicador</h3>
          <p>Distribui conteúdo automaticamente nas plataformas certas no momento ideal.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=600&q=80" alt="Social Media Publishing"/>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <h3>Maestro</h3>
          <p>Orquestra todos os agentes, garantindo sincronia e qualidade final.</p>
          <div class="feature-image">
            <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&q=80" alt="Team Orchestration"/>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- How it Works -->
  <section id="how" class="how-it-works">
    <div class="container">
      <div class="features-header">
        <h2>Como o <span class="gradient-text">MaestroIA</span> Funciona</h2>
        <p>Em 4 passos simples você coloca seus agentes de IA para trabalhar</p>
      </div>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3>Defina seu Objetivo</h3>
          <p>Informe seu produto, público-alvo e metas de campanha</p>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <h3>IA Pesquisa</h3>
          <p>Agentes analisam mercado, tendências e concorrência</p>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <h3>Conteúdo é Criado</h3>
          <p>Textos, estratégias e criativos são gerados automaticamente</p>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <h3>Publicação Automática</h3>
          <p>Campanhas são publicadas e otimizadas em tempo real</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Showcase -->
  <section>
    <div class="container">
      <div class="showcase-grid">
        <div class="showcase-image">
          <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80" alt="Team working with AI"/>
        </div>
        <div class="showcase-content">
          <h2>Escale seu Marketing <span class="gradient-text">Sem Escalar Custos</span></h2>
          <p>Empresas que usam MaestroIA conseguem produzir 10x mais conteúdo com a mesma equipe, reduzindo custos operacionais em até 85%.</p>
          <ul class="showcase-list">
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>Produção de conteúdo 24 horas por dia, 7 dias por semana</span>
            </li>
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>Consistência de marca em todos os canais automaticamente</span>
            </li>
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>Análise de performance integrada com sugestões de melhoria</span>
            </li>
            <li>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>Integrações nativas com Google Ads, Meta e mais</span>
            </li>
          </ul>
          <a href="/app" class="btn btn-primary">Explorar Recursos</a>
        </div>
      </div>
    </div>
  </section>

  <!-- Pricing -->
  <section id="pricing" class="pricing">
    <div class="container">
      <div class="pricing-header">
        <h2>Planos para <span class="gradient-text">Cada Momento</span></h2>
        <p>Comece gratuitamente e escale conforme seu negócio cresce</p>
      </div>
      <div class="pricing-grid">
        <div class="pricing-card">
          <div class="pricing-name">Starter</div>
          <div class="pricing-desc">Para quem está começando</div>
          <div class="pricing-price">Grátis</div>
          <ul class="pricing-features">
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>50 execuções/mês</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>3 agentes ativos</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>1 integração</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Suporte por email</li>
          </ul>
          <a href="/app" class="btn btn-secondary">Começar Grátis</a>
        </div>
        <div class="pricing-card featured">
          <div class="pricing-name">Pro</div>
          <div class="pricing-desc">Para equipes em crescimento</div>
          <div class="pricing-price">R$297<span>/mês</span></div>
          <ul class="pricing-features">
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Execuções ilimitadas</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Todos os 6 agentes</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Todas as integrações</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Suporte prioritário</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>API access</li>
          </ul>
          <a href="/app" class="btn btn-primary">Assinar Pro</a>
        </div>
        <div class="pricing-card">
          <div class="pricing-name">Enterprise</div>
          <div class="pricing-desc">Para grandes operações</div>
          <div class="pricing-price">Custom</div>
          <ul class="pricing-features">
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Tudo do Pro</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Agentes customizados</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>SLA garantido</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Onboarding dedicado</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>White-label</li>
          </ul>
          <a href="/app" class="btn btn-secondary">Falar com Vendas</a>
        </div>
      </div>
    </div>
  </section>

  <!-- Testimonials -->
  <section>
    <div class="container">
      <div class="testimonials-header">
        <h2>O que nossos <span class="gradient-text">Clientes Dizem</span></h2>
        <p>Empresas de todos os tamanhos já transformaram seu marketing com MaestroIA</p>
      </div>
      <div class="testimonials-grid">
        <div class="testimonial-card">
          <div class="testimonial-stars">★★★★★</div>
          <p class="testimonial-text">"Reduzimos nosso tempo de criação de campanhas de 3 dias para 2 horas. O ROI foi absurdo no primeiro mês."</p>
          <div class="testimonial-author">
            <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80" alt="João Silva"/>
            <div class="testimonial-info">
              <h4>João Silva</h4>
              <p>CEO, TechStart</p>
            </div>
          </div>
        </div>
        <div class="testimonial-card">
          <div class="testimonial-stars">★★★★★</div>
          <p class="testimonial-text">"A qualidade do conteúdo gerado é impressionante. Parece que temos uma agência inteira trabalhando 24h."</p>
          <div class="testimonial-author">
            <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&q=80" alt="Maria Santos"/>
            <div class="testimonial-info">
              <h4>Maria Santos</h4>
              <p>CMO, E-commerce Plus</p>
            </div>
          </div>
        </div>
        <div class="testimonial-card">
          <div class="testimonial-stars">★★★★★</div>
          <p class="testimonial-text">"Finalmente uma ferramenta de IA que realmente entrega resultados. Escalamos 5x sem aumentar a equipe."</p>
          <div class="testimonial-author">
            <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80" alt="Pedro Costa"/>
            <div class="testimonial-info">
              <h4>Pedro Costa</h4>
              <p>Founder, GrowthLab</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section id="faq" class="faq">
    <div class="container">
      <div class="faq-header">
        <h2>Perguntas <span class="gradient-text">Frequentes</span></h2>
        <p>Tudo que você precisa saber antes de começar</p>
      </div>
      <div class="faq-grid">
        <div class="faq-item active">
          <div class="faq-question">
            Como o MaestroIA é diferente de outras ferramentas de IA?
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </div>
          <div class="faq-answer">MaestroIA não é apenas uma ferramenta de geração de texto. É um sistema completo de orquestração com 6 agentes especializados que trabalham em conjunto, cada um focado em uma etapa específica do funil de marketing, garantindo resultados muito superiores.</div>
        </div>
        <div class="faq-item">
          <div class="faq-question">
            Preciso de conhecimento técnico para usar?
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </div>
          <div class="faq-answer">Não! A plataforma foi desenhada para ser intuitiva. Basta informar seu objetivo e deixar os agentes trabalharem. Mas se você é técnico, temos API completa para integrações avançadas.</div>
        </div>
        <div class="faq-item">
          <div class="faq-question">
            Posso cancelar a qualquer momento?
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </div>
          <div class="faq-answer">Sim, você pode cancelar sua assinatura a qualquer momento sem multas ou taxas. Seu acesso continua até o fim do período pago.</div>
        </div>
        <div class="faq-item">
          <div class="faq-question">
            Quais plataformas são suportadas?
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </div>
          <div class="faq-answer">Atualmente integramos com Google Ads, Meta (Facebook/Instagram), LinkedIn, e estamos constantemente adicionando novas plataformas como TikTok e Twitter/X.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="cta">
    <div class="container">
      <div class="cta-box">
        <div class="cta-content">
          <h2>Pronto para Revolucionar seu Marketing?</h2>
          <p>Junte-se a centenas de empresas que já estão usando IA para escalar seus resultados</p>
          <div class="cta-buttons">
            <a href="/app" class="btn btn-primary">Começar Gratuitamente</a>
            <a href="#pricing" class="btn btn-secondary">Ver Planos</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="#" class="logo">
            <svg width="32" height="32" viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="url(#lg2)" stroke-width="3"/><path d="M14 20l4 4 8-8" stroke="url(#lg2)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="lg2" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#d946ef"/></linearGradient></defs></svg>
            MaestroIA
          </a>
          <p>Orquestração inteligente de agentes de IA para automatizar e escalar seu marketing digital.</p>
          <div class="footer-social">
            <a href="#"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg></a>
            <a href="#"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg></a>
            <a href="#"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
          </div>
        </div>
        <div class="footer-links">
          <h4>Produto</h4>
          <a href="#features">Recursos</a>
          <a href="#pricing">Preços</a>
          <a href="/docs">Documentação</a>
          <a href="/docs">API</a>
        </div>
        <div class="footer-links">
          <h4>Empresa</h4>
          <a href="#">Sobre</a>
          <a href="#">Blog</a>
          <a href="#">Carreiras</a>
          <a href="#">Contato</a>
        </div>
        <div class="footer-links">
          <h4>Legal</h4>
          <a href="#">Termos de Uso</a>
          <a href="#">Privacidade</a>
          <a href="#">Cookies</a>
          <a href="#">LGPD</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 MaestroIA. Todos os direitos reservados.</span>
        <a href="/health">Status do Sistema</a>
      </div>
    </div>
  </footer>

  <script>
    // Header scroll effect
    window.addEventListener('scroll',()=>{
      document.getElementById('header').classList.toggle('scrolled',window.scrollY>50)
    });
    // FAQ accordion
    document.querySelectorAll('.faq-question').forEach(q=>{
      q.addEventListener('click',()=>{
        q.parentElement.classList.toggle('active')
      })
    });
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(a=>{
      a.addEventListener('click',e=>{
        e.preventDefault();
        document.querySelector(a.getAttribute('href'))?.scrollIntoView({behavior:'smooth'})
      })
    });
  </script>
</body>
</html>
        """
    )


@app.get("/health")
def healthcheck():
	return {
		"status": "ok",
		"service": "maestroia-api",
		"deployment": "vercel",
	}


@app.get("/api/status")
def api_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "agents": ["pesquisador", "estrategista", "criador_conteudo", "publicador", "otimizador", "maestro"],
        "features": ["campaigns", "scheduling", "analytics", "integrations"]
    }


@app.get("/app")
def app_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>MaestroIA — Plataforma</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    :root{
      --bg:#030712;--bg2:#0f172a;--bg3:#1e293b;
      --text:#f1f5f9;--text2:#94a3b8;--text3:#64748b;
      --primary:#6366f1;--primary-hover:#818cf8;--primary-glow:rgba(99,102,241,.35);
      --accent:#22d3ee;--success:#10b981;--warning:#f59e0b;--danger:#ef4444;
      --glass:rgba(15,23,42,.7);--border:rgba(148,163,184,.12);
      --gradient:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#d946ef 100%);
    }
    body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
    .bg-grid{position:fixed;inset:0;background-image:radial-gradient(rgba(99,102,241,.1) 1px,transparent 1px);background-size:50px 50px;pointer-events:none;z-index:-1}
    
    /* Layout */
    .app-container{display:flex;min-height:100vh}
    
    /* Sidebar */
    .sidebar{width:280px;background:var(--bg2);border-right:1px solid var(--border);padding:24px;display:flex;flex-direction:column}
    .sidebar-logo{display:flex;align-items:center;gap:12px;font-size:1.5rem;font-weight:800;margin-bottom:32px;color:var(--text)}
    .sidebar-logo svg{width:36px;height:36px}
    .sidebar-nav{flex:1}
    .nav-section{margin-bottom:24px}
    .nav-section-title{font-size:.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:12px;padding:0 12px}
    .nav-item{display:flex;align-items:center;gap:12px;padding:12px;border-radius:10px;color:var(--text2);text-decoration:none;transition:all .2s;margin-bottom:4px;cursor:pointer}
    .nav-item:hover,.nav-item.active{background:var(--bg3);color:var(--text)}
    .nav-item.active{background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(139,92,246,.2));border:1px solid var(--primary)}
    .nav-item svg{width:20px;height:20px}
    .sidebar-footer{padding-top:24px;border-top:1px solid var(--border)}
    .user-info{display:flex;align-items:center;gap:12px;padding:12px;border-radius:10px;background:var(--bg3)}
    .user-avatar{width:40px;height:40px;border-radius:50%;background:var(--gradient);display:flex;align-items:center;justify-content:center;font-weight:700}
    .user-name{font-weight:600;font-size:.9rem}
    .user-plan{font-size:.75rem;color:var(--text3)}
    
    /* Loading Spinner */
    .loading-spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto}
    @keyframes spin{to{transform:rotate(360deg)}}
    
    /* Main Content */
    .main-content{flex:1;padding:32px;overflow-y:auto}
    .page-header{margin-bottom:32px}
    .page-title{font-size:2rem;font-weight:800;margin-bottom:8px}
    .page-subtitle{color:var(--text2)}
    
    /* Cards */
    .cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;margin-bottom:32px}
    .card{background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px;transition:all .3s}
    .card:hover{border-color:var(--primary);transform:translateY(-2px)}
    .card-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:16px}
    .card-icon.blue{background:linear-gradient(135deg,#6366f1,#8b5cf6)}
    .card-icon.green{background:linear-gradient(135deg,#10b981,#22d3ee)}
    .card-icon.orange{background:linear-gradient(135deg,#f59e0b,#ef4444)}
    .card-icon.purple{background:linear-gradient(135deg,#8b5cf6,#d946ef)}
    .card-icon svg{width:24px;height:24px;color:#fff}
    .card-title{font-size:1.1rem;font-weight:600;margin-bottom:8px}
    .card-value{font-size:2rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .card-change{font-size:.85rem;color:var(--success);margin-top:8px}
    .card-change.negative{color:var(--danger)}
    
    /* Stats Section */
    .stats-section{background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:32px}
    .stats-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
    .stats-title{font-size:1.25rem;font-weight:700}
    .stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
    .stat-item{text-align:center;padding:16px;background:var(--bg3);border-radius:12px}
    .stat-value{font-size:1.5rem;font-weight:800;color:var(--primary)}
    .stat-label{font-size:.85rem;color:var(--text2);margin-top:4px}
    
    /* Quick Actions */
    .quick-actions{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:32px}
    .action-btn{display:flex;align-items:center;gap:12px;padding:16px 20px;background:var(--gradient);border:none;border-radius:12px;color:#fff;font-weight:600;font-size:1rem;cursor:pointer;transition:all .3s}
    .action-btn:hover{transform:translateY(-2px);box-shadow:0 8px 30px var(--primary-glow)}
    .action-btn.secondary{background:var(--glass);border:1px solid var(--border)}
    .action-btn.secondary:hover{border-color:var(--primary)}
    .action-btn svg{width:20px;height:20px}
    
    /* Recent Activity */
    .activity-section{background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px}
    .activity-title{font-size:1.25rem;font-weight:700;margin-bottom:20px}
    .activity-list{display:flex;flex-direction:column;gap:12px}
    .activity-item{display:flex;align-items:center;gap:16px;padding:16px;background:var(--bg3);border-radius:12px}
    .activity-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
    .activity-icon.campaign{background:rgba(99,102,241,.2);color:var(--primary)}
    .activity-icon.publish{background:rgba(16,185,129,.2);color:var(--success)}
    .activity-icon.optimize{background:rgba(245,158,11,.2);color:var(--warning)}
    .activity-content{flex:1}
    .activity-text{font-weight:500}
    .activity-time{font-size:.85rem;color:var(--text3)}
    
    /* Login Form */
    .login-container{max-width:440px;margin:0 auto;padding:60px 24px}
    .login-card{background:var(--glass);border:1px solid var(--border);border-radius:24px;padding:40px}
    .login-header{text-align:center;margin-bottom:32px}
    .login-logo{display:flex;align-items:center;justify-content:center;gap:12px;font-size:1.75rem;font-weight:800;margin-bottom:16px}
    .login-logo svg{width:44px;height:44px}
    .login-title{font-size:1.5rem;font-weight:700;margin-bottom:8px}
    .login-subtitle{color:var(--text2)}
    .form-group{margin-bottom:20px}
    .form-label{display:block;font-size:.9rem;font-weight:500;margin-bottom:8px;color:var(--text2)}
    .form-input{width:100%;padding:14px 16px;background:var(--bg3);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:1rem;transition:all .2s}
    .form-input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-glow)}
    .form-input::placeholder{color:var(--text3)}
    .btn-login{width:100%;padding:16px;background:var(--gradient);border:none;border-radius:12px;color:#fff;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;margin-top:8px}
    .btn-login:hover{transform:translateY(-2px);box-shadow:0 8px 30px var(--primary-glow)}
    .login-footer{text-align:center;margin-top:24px;color:var(--text2);font-size:.9rem}
    .login-footer a{color:var(--primary);text-decoration:none}
    .login-footer a:hover{text-decoration:underline}
    .divider{display:flex;align-items:center;gap:16px;margin:24px 0;color:var(--text3);font-size:.85rem}
    .divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border)}
    .social-login{display:flex;gap:12px}
    .social-btn{flex:1;padding:12px;background:var(--bg3);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.9rem;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:8px}
    .social-btn:hover{border-color:var(--primary);background:var(--bg2)}
    
    /* Tabs */
    .tabs{display:flex;gap:8px;margin-bottom:24px;border-bottom:1px solid var(--border);padding-bottom:16px}
    .tab{padding:12px 20px;background:transparent;border:none;color:var(--text2);font-size:.95rem;font-weight:500;cursor:pointer;border-radius:8px;transition:all .2s}
    .tab:hover{color:var(--text);background:var(--bg3)}
    .tab.active{color:var(--text);background:var(--bg3)}
    
    /* Responsive */
    @media(max-width:1024px){
      .sidebar{width:240px}
      .stats-grid{grid-template-columns:repeat(2,1fr)}
    }
    @media(max-width:768px){
      .app-container{flex-direction:column}
      .sidebar{width:100%;border-right:none;border-bottom:1px solid var(--border)}
      .sidebar-nav{display:flex;gap:8px;overflow-x:auto;padding-bottom:16px}
      .nav-section{margin-bottom:0}
      .nav-section-title{display:none}
      .stats-grid{grid-template-columns:1fr 1fr}
    }
  </style>
</head>
<body>
  <div class="bg-grid"></div>
  
  <div id="app-root">
    <!-- Login View (shown by default) -->
    <div id="login-view" class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <svg viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="url(#lg)" stroke-width="3"/><path d="M14 20l4 4 8-8" stroke="url(#lg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="lg" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#d946ef"/></linearGradient></defs></svg>
            MaestroIA
          </div>
          <h1 class="login-title">Bem-vindo de volta</h1>
          <p class="login-subtitle">Entre para acessar sua plataforma</p>
        </div>
        
        <form id="login-form">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" class="form-input" placeholder="seu@email.com" required/>
          </div>
          <div class="form-group">
            <label class="form-label">Senha</label>
            <input type="password" class="form-input" placeholder="••••••••" required/>
          </div>
          <button type="submit" class="btn-login">Entrar na Plataforma</button>
        </form>
        
        <div class="divider">ou continue com</div>
        
        <div class="social-login">
          <button type="button" class="social-btn" onclick="loginWithGoogle()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Google
          </button>
          <button type="button" class="social-btn" onclick="loginWithGitHub()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
            GitHub
          </button>
        </div>
        
        <div class="login-footer">
          <p>Não tem conta? <a href="#" onclick="showRegister()">Criar conta grátis</a></p>
          <p style="margin-top:12px"><a href="/">← Voltar ao site</a></p>
        </div>
      </div>
    </div>
    
    <!-- Dashboard View (hidden by default) -->
    <div id="dashboard-view" class="app-container" style="display:none">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-logo">
          <svg viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="url(#lg2)" stroke-width="3"/><path d="M14 20l4 4 8-8" stroke="url(#lg2)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="lg2" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#d946ef"/></linearGradient></defs></svg>
          MaestroIA
        </div>
        
        <nav class="sidebar-nav">
          <div class="nav-section">
            <div class="nav-section-title">Principal</div>
            <a href="#" class="nav-item active" data-page="dashboard">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              Dashboard
            </a>
            <a href="#" class="nav-item" data-page="campanhas">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Campanhas
            </a>
            <a href="#" class="nav-item" data-page="agendamento">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              Agendamento
            </a>
            <a href="#" class="nav-item" data-page="analytics">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              Analytics
            </a>
          </div>
          
          <div class="nav-section">
            <div class="nav-section-title">Agentes IA</div>
            <a href="#" class="nav-item" data-page="pesquisador">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              Pesquisador
            </a>
            <a href="#" class="nav-item" data-page="estrategista">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              Estrategista
            </a>
            <a href="#" class="nav-item" data-page="criador">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/></svg>
              Criador
            </a>
          </div>
          
          <div class="nav-section">
            <div class="nav-section-title">Configurações</div>
            <a href="#" class="nav-item" data-page="configuracoes">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              Configurações
            </a>
            <a href="#" class="nav-item" data-page="integracoes">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              Integrações
            </a>
            <a href="/docs" class="nav-item" target="_blank">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              API Docs
            </a>
          </div>
        </nav>
        
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">U</div>
            <div>
              <div class="user-name">Carregando...</div>
              <div class="user-plan">-</div>
            </div>
          </div>
          <button onclick="logout()" style="width:100%;margin-top:12px;padding:10px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;color:var(--text2);cursor:pointer;font-size:.85rem">Sair</button>
        </div>
      </aside>
      
      <!-- Main Content -->
      <main class="main-content">
        <!-- PAGE: Dashboard -->
        <div id="page-dashboard" class="page-content">
          <div class="page-header">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Visão geral da sua conta</p>
          </div>
          
          <div class="quick-actions">
            <button class="action-btn" onclick="navigateTo('campanhas')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Nova Campanha
            </button>
            <button class="action-btn secondary" onclick="navigateTo('agendamento')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>
              Agendar Post
            </button>
            <button class="action-btn secondary" onclick="navigateTo('pesquisador')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              Pesquisar Mercado
            </button>
          </div>
          
          <div class="empty-state" style="text-align:center;padding:60px 20px;background:var(--glass);border:1px solid var(--border);border-radius:16px;margin-top:24px">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text3)" stroke-width="1.5" style="margin-bottom:20px"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
            <h3 style="font-size:1.25rem;font-weight:600;margin-bottom:8px;color:var(--text)">Nenhuma campanha ainda</h3>
            <p style="color:var(--text2);margin-bottom:24px">Crie sua primeira campanha para começar a automatizar seu marketing com IA</p>
            <button class="action-btn" onclick="navigateTo('campanhas')" style="display:inline-flex">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Criar Primeira Campanha
            </button>
          </div>
        </div>
        
        <!-- PAGE: Campanhas -->
        <div id="page-campanhas" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Campanhas</h1>
            <p class="page-subtitle">Gerencie suas campanhas de marketing</p>
          </div>
          
          <div class="campaign-form" style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:20px">Criar Nova Campanha</h3>
            <form id="campaign-form" onsubmit="createCampaign(event)">
              <div class="form-group">
                <label class="form-label">Nome da Campanha</label>
                <input type="text" class="form-input" id="campaign-name" placeholder="Ex: Lançamento Produto X" required/>
              </div>
              <div class="form-group">
                <label class="form-label">Objetivo</label>
                <select class="form-input" id="campaign-objetivo" required>
                  <option value="">Selecione o objetivo</option>
                  <option value="awareness">Aumentar reconhecimento de marca</option>
                  <option value="engagement">Gerar engajamento</option>
                  <option value="leads">Captar leads</option>
                  <option value="sales">Aumentar vendas</option>
                  <option value="traffic">Gerar tráfego</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Público-alvo</label>
                <input type="text" class="form-input" id="campaign-publico" placeholder="Ex: Empreendedores de 25-45 anos interessados em tecnologia" required/>
              </div>
              <div class="form-group">
                <label class="form-label">Produto/Serviço</label>
                <textarea class="form-input" id="campaign-produto" rows="3" placeholder="Descreva seu produto ou serviço..." required></textarea>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
                <div class="form-group">
                  <label class="form-label">Orçamento (R$)</label>
                  <input type="number" class="form-input" id="campaign-orcamento" placeholder="0.00" min="0" step="0.01"/>
                </div>
                <div class="form-group">
                  <label class="form-label">Canais</label>
                  <select class="form-input" id="campaign-canais" multiple style="height:auto;min-height:44px">
                    <option value="instagram" selected>Instagram</option>
                    <option value="facebook" selected>Facebook</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="twitter">Twitter/X</option>
                    <option value="tiktok">TikTok</option>
                    <option value="google">Google Ads</option>
                  </select>
                </div>
              </div>
              <button type="submit" class="action-btn" style="width:100%;margin-top:16px;justify-content:center">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                Executar Campanha com IA
              </button>
            </form>
          </div>
          
          <div id="campaigns-list">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:16px">Histórico de Campanhas</h3>
            <div id="campaigns-empty" class="empty-state" style="text-align:center;padding:40px 20px;background:var(--bg3);border-radius:12px">
              <p style="color:var(--text2)">Nenhuma campanha executada ainda</p>
            </div>
            <div id="campaigns-data" style="display:none"></div>
          </div>
        </div>
        
        <!-- PAGE: Agendamento -->
        <div id="page-agendamento" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Agendamento</h1>
            <p class="page-subtitle">Programe publicações automáticas</p>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:20px">Agendar Publicação</h3>
            <form id="schedule-form" onsubmit="schedulePost(event)">
              <div class="form-group">
                <label class="form-label">Conteúdo</label>
                <textarea class="form-input" id="schedule-content" rows="4" placeholder="Digite o conteúdo da publicação..." required></textarea>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
                <div class="form-group">
                  <label class="form-label">Data</label>
                  <input type="date" class="form-input" id="schedule-date" required/>
                </div>
                <div class="form-group">
                  <label class="form-label">Horário</label>
                  <input type="time" class="form-input" id="schedule-time" required/>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Plataformas</label>
                <div style="display:flex;gap:12px;flex-wrap:wrap">
                  <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:8px 16px;background:var(--bg3);border-radius:8px">
                    <input type="checkbox" name="platforms" value="instagram" checked/> Instagram
                  </label>
                  <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:8px 16px;background:var(--bg3);border-radius:8px">
                    <input type="checkbox" name="platforms" value="facebook" checked/> Facebook
                  </label>
                  <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:8px 16px;background:var(--bg3);border-radius:8px">
                    <input type="checkbox" name="platforms" value="linkedin"/> LinkedIn
                  </label>
                  <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:8px 16px;background:var(--bg3);border-radius:8px">
                    <input type="checkbox" name="platforms" value="twitter"/> Twitter/X
                  </label>
                </div>
              </div>
              <button type="submit" class="action-btn" style="width:100%;margin-top:8px;justify-content:center">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>
                Agendar Publicação
              </button>
            </form>
          </div>
          
          <div style="margin-top:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:16px">Publicações Agendadas</h3>
            <div class="empty-state" style="text-align:center;padding:40px 20px;background:var(--bg3);border-radius:12px">
              <p style="color:var(--text2)">Nenhuma publicação agendada</p>
            </div>
          </div>
        </div>
        
        <!-- PAGE: Analytics -->
        <div id="page-analytics" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Analytics</h1>
            <p class="page-subtitle">Métricas e performance das campanhas</p>
          </div>
          
          <div class="empty-state" style="text-align:center;padding:60px 20px;background:var(--glass);border:1px solid var(--border);border-radius:16px">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text3)" stroke-width="1.5" style="margin-bottom:20px"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            <h3 style="font-size:1.25rem;font-weight:600;margin-bottom:8px;color:var(--text)">Sem dados ainda</h3>
            <p style="color:var(--text2);margin-bottom:24px">Execute campanhas para começar a coletar métricas de performance</p>
            <button class="action-btn" onclick="navigateTo('campanhas')" style="display:inline-flex">Ir para Campanhas</button>
          </div>
        </div>
        
        <!-- PAGE: Pesquisador -->
        <div id="page-pesquisador" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Agente Pesquisador</h1>
            <p class="page-subtitle">Pesquisa de mercado e tendências com IA</p>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <form id="research-form" onsubmit="runResearch(event)">
              <div class="form-group">
                <label class="form-label">O que você quer pesquisar?</label>
                <textarea class="form-input" id="research-query" rows="3" placeholder="Ex: Tendências de marketing digital para e-commerce em 2026" required></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Nicho/Indústria</label>
                <input type="text" class="form-input" id="research-niche" placeholder="Ex: E-commerce, SaaS, Varejo..."/>
              </div>
              <button type="submit" class="action-btn" style="width:100%;justify-content:center">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                Iniciar Pesquisa
              </button>
            </form>
          </div>
          
          <div id="research-result" style="display:none;margin-top:24px;background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:16px">Resultado da Pesquisa</h3>
            <div id="research-content" style="color:var(--text2);line-height:1.8;white-space:pre-wrap"></div>
          </div>
        </div>
        
        <!-- PAGE: Estrategista -->
        <div id="page-estrategista" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Agente Estrategista</h1>
            <p class="page-subtitle">Criação de estratégias de marketing com IA</p>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <form id="strategy-form" onsubmit="runStrategy(event)">
              <div class="form-group">
                <label class="form-label">Objetivo da estratégia</label>
                <select class="form-input" id="strategy-objetivo" required>
                  <option value="">Selecione</option>
                  <option value="lancamento">Lançamento de produto</option>
                  <option value="branding">Construção de marca</option>
                  <option value="leads">Geração de leads</option>
                  <option value="vendas">Aumento de vendas</option>
                  <option value="engajamento">Engajamento de audiência</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Descrição do negócio</label>
                <textarea class="form-input" id="strategy-negocio" rows="3" placeholder="Descreva seu negócio, produto e diferenciais..." required></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Público-alvo</label>
                <input type="text" class="form-input" id="strategy-publico" placeholder="Quem é seu cliente ideal?" required/>
              </div>
              <button type="submit" class="action-btn" style="width:100%;justify-content:center">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Gerar Estratégia
              </button>
            </form>
          </div>
          
          <div id="strategy-result" style="display:none;margin-top:24px;background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:16px">Estratégia Gerada</h3>
            <div id="strategy-content" style="color:var(--text2);line-height:1.8;white-space:pre-wrap"></div>
          </div>
        </div>
        
        <!-- PAGE: Criador -->
        <div id="page-criador" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Agente Criador</h1>
            <p class="page-subtitle">Geração de conteúdo com IA</p>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <form id="content-form" onsubmit="runContentCreator(event)">
              <div class="form-group">
                <label class="form-label">Tipo de conteúdo</label>
                <select class="form-input" id="content-tipo" required>
                  <option value="">Selecione</option>
                  <option value="post-instagram">Post para Instagram</option>
                  <option value="post-linkedin">Post para LinkedIn</option>
                  <option value="ad-copy">Copy para anúncio</option>
                  <option value="email">Email marketing</option>
                  <option value="blog">Artigo de blog</option>
                  <option value="script">Script para vídeo</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Tema/Assunto</label>
                <input type="text" class="form-input" id="content-tema" placeholder="Sobre o que é o conteúdo?" required/>
              </div>
              <div class="form-group">
                <label class="form-label">Tom de voz</label>
                <select class="form-input" id="content-tom">
                  <option value="profissional">Profissional</option>
                  <option value="casual">Casual</option>
                  <option value="inspirador">Inspirador</option>
                  <option value="educativo">Educativo</option>
                  <option value="divertido">Divertido</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Informações adicionais (opcional)</label>
                <textarea class="form-input" id="content-info" rows="2" placeholder="Palavras-chave, CTAs específicos, etc."></textarea>
              </div>
              <button type="submit" class="action-btn" style="width:100%;justify-content:center">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/></svg>
                Gerar Conteúdo
              </button>
            </form>
          </div>
          
          <div id="content-result" style="display:none;margin-top:24px;background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
              <h3 style="font-size:1.1rem;font-weight:600">Conteúdo Gerado</h3>
              <button onclick="copyContent()" class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Copiar</button>
            </div>
            <div id="content-output" style="color:var(--text);line-height:1.8;white-space:pre-wrap;background:var(--bg3);padding:20px;border-radius:12px"></div>
          </div>
        </div>
        
        <!-- PAGE: Configurações -->
        <div id="page-configuracoes" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Configurações</h1>
            <p class="page-subtitle">Gerencie sua conta e preferências</p>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:20px">Informações da Conta</h3>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input type="email" class="form-input" id="config-email" disabled/>
            </div>
            <div class="form-group">
              <label class="form-label">Nome</label>
              <input type="text" class="form-input" id="config-name"/>
            </div>
            <button class="action-btn secondary" style="margin-top:8px">Salvar Alterações</button>
          </div>
          
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px">
            <h3 style="font-size:1.1rem;font-weight:600;margin-bottom:20px">Plano Atual</h3>
            <div style="display:flex;align-items:center;justify-content:space-between;padding:16px;background:var(--bg3);border-radius:12px">
              <div>
                <div style="font-weight:600" id="config-plan">Free</div>
                <div style="color:var(--text2);font-size:.9rem">Recursos básicos</div>
              </div>
              <a href="/#pricing" class="action-btn" style="padding:10px 20px;font-size:.9rem">Fazer Upgrade</a>
            </div>
          </div>
        </div>
        
        <!-- PAGE: Integrações -->
        <div id="page-integracoes" class="page-content" style="display:none">
          <div class="page-header">
            <h1 class="page-title">Integrações</h1>
            <p class="page-subtitle">Conecte suas redes sociais e ferramentas</p>
          </div>
          
          <div class="cards-grid">
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">Instagram</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
            
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:#1877f2;border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">Facebook</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
            
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:#0a66c2;border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">LinkedIn</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
            
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:#000;border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">Twitter / X</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
            
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:#000;border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">TikTok</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
            
            <div class="card" style="display:flex;align-items:center;gap:16px">
              <div style="width:48px;height:48px;background:#4285f4;border-radius:12px;display:flex;align-items:center;justify-content:center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              </div>
              <div style="flex:1">
                <div style="font-weight:600">Google Ads</div>
                <div style="color:var(--text2);font-size:.85rem">Não conectado</div>
              </div>
              <button class="action-btn secondary" style="padding:8px 16px;font-size:.85rem">Conectar</button>
            </div>
          </div>
        </div>
        
      </main>
    </div>
  </div>
  
  <script>
    // Global user data
    let currentUser = null;
    
    // OAuth Login Functions
    function loginWithGoogle() {
      // Check if configured first
      fetch('/auth/status')
        .then(r => r.json())
        .then(status => {
          if (status.google && status.google.configured) {
            window.location.href = '/auth/google/start';
          } else {
            alert('Login com Google ainda não foi configurado.\\n\\nPara configurar:\\n1. Crie credenciais em console.cloud.google.com\\n2. Adicione GOOGLE_OAUTH_CLIENT_ID e GOOGLE_OAUTH_CLIENT_SECRET nas variáveis de ambiente');
          }
        })
        .catch(() => {
          // Fallback - try anyway
          window.location.href = '/auth/google/start';
        });
    }
    
    function loginWithGitHub() {
      // Check if configured first
      fetch('/auth/status')
        .then(r => r.json())
        .then(status => {
          if (status.github && status.github.configured) {
            window.location.href = '/auth/github/start';
          } else {
            alert('Login com GitHub ainda não foi configurado.\\n\\nPara configurar:\\n1. Crie OAuth App em github.com/settings/developers\\n2. Adicione GITHUB_OAUTH_CLIENT_ID e GITHUB_OAUTH_CLIENT_SECRET nas variáveis de ambiente');
          }
        })
        .catch(() => {
          // Fallback - try anyway
          window.location.href = '/auth/github/start';
        });
    }
    
    // Process OAuth callback parameters
    function processOAuthCallback() {
      const params = new URLSearchParams(window.location.search);
      const login = params.get('login');
      const error = params.get('error');
      
      if (error) {
        alert('Erro no login: ' + error);
        // Clean URL
        window.history.replaceState({}, document.title, '/app');
        return false;
      }
      
      if (login === 'success') {
        const provider = params.get('provider');
        const name = params.get('name');
        const email = params.get('email');
        const picture = params.get('picture');
        
        currentUser = { provider, name, email, picture };
        
        // Update UI with user info
        updateUserInfo(name, email, picture, provider);
        
        // Show dashboard
        showDashboard();
        
        // Clean URL
        window.history.replaceState({}, document.title, '/app');
        return true;
      }
      
      return false;
    }
    
    // Update user info in sidebar
    function updateUserInfo(name, email, picture, provider) {
      const userAvatar = document.querySelector('.user-avatar');
      const userName = document.querySelector('.user-name');
      const userPlan = document.querySelector('.user-plan');
      
      if (userName) userName.textContent = name || 'Usuário';
      if (userPlan) userPlan.textContent = provider ? ('via ' + provider.charAt(0).toUpperCase() + provider.slice(1)) : 'Plano Free';
      
      if (userAvatar && picture) {
        userAvatar.innerHTML = '<img src="' + picture + '" alt="Avatar" style="width:100%;height:100%;border-radius:50%;object-fit:cover"/>';
      }
    }
    
    // Show dashboard view
    function showDashboard() {
      const loginView = document.getElementById('login-view');
      const dashboardView = document.getElementById('dashboard-view');
      if (loginView) loginView.style.display = 'none';
      if (dashboardView) dashboardView.style.display = 'flex';
    }
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
      // Check for OAuth callback first
      if (processOAuthCallback()) {
        return; // Already logged in via OAuth
      }
      
      const loginForm = document.getElementById('login-form');
      const loginView = document.getElementById('login-view');
      const dashboardView = document.getElementById('dashboard-view');
      
      if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          // Get form values
          const email = loginForm.querySelector('input[type="email"]').value;
          const password = loginForm.querySelector('input[type="password"]').value;
          
          // Simple validation
          if (!email || !password) {
            alert('Por favor, preencha todos os campos.');
            return false;
          }
          
          // Update user info
          const emailName = email.split('@')[0];
          updateUserInfo(emailName, email, null, null);
          
          // Show dashboard
          showDashboard();
          
          return false;
        });
      }
      
      // Nav item clicks with page navigation
      document.querySelectorAll('.nav-item[data-page]').forEach(item => {
        item.addEventListener('click', function(e) {
          e.preventDefault();
          const page = this.getAttribute('data-page');
          if (page) navigateTo(page);
        });
      });
      
      // Update config fields if user is logged in
      if (currentUser) {
        const configEmail = document.getElementById('config-email');
        const configName = document.getElementById('config-name');
        if (configEmail) configEmail.value = currentUser.email || '';
        if (configName) configName.value = currentUser.name || '';
      }
    });
    
    // Page Navigation
    function navigateTo(page) {
      // Hide all pages
      document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
      
      // Show target page
      const targetPage = document.getElementById('page-' + page);
      if (targetPage) targetPage.style.display = 'block';
      
      // Update nav active state
      document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-page') === page) {
          item.classList.add('active');
        }
      });
    }
    
    // Logout function
    function logout() {
      currentUser = null;
      const loginView = document.getElementById('login-view');
      const dashboardView = document.getElementById('dashboard-view');
      if (loginView) loginView.style.display = 'flex';
      if (dashboardView) dashboardView.style.display = 'none';
      // Clear form
      const loginForm = document.getElementById('login-form');
      if (loginForm) loginForm.reset();
    }
    
    // Create Campaign
    function createCampaign(e) {
      e.preventDefault();
      const nome = document.getElementById('campaign-name').value;
      const objetivo = document.getElementById('campaign-objetivo').value;
      const publico = document.getElementById('campaign-publico').value;
      const produto = document.getElementById('campaign-produto').value;
      const orcamento = document.getElementById('campaign-orcamento').value;
      
      if (!nome || !objetivo || !publico || !produto) {
        alert('Por favor, preencha os campos obrigatórios.');
        return;
      }
      
      // Show loading
      const btn = document.querySelector('#campaign-form button[type="submit"]');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Processando...';
      btn.disabled = true;
      
      // Simulate API call
      setTimeout(() => {
        // Add to campaigns list
        const campaignsEmpty = document.getElementById('campaigns-empty');
        const campaignsData = document.getElementById('campaigns-data');
        if (campaignsEmpty) campaignsEmpty.style.display = 'none';
        if (campaignsData) {
          campaignsData.style.display = 'block';
          const newCampaign = document.createElement('div');
          newCampaign.style = 'background:var(--bg3);padding:16px;border-radius:12px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center';
          newCampaign.innerHTML = '<div><strong>' + nome + '</strong><br/><span style="color:var(--text2);font-size:.85rem">' + objetivo + ' • ' + new Date().toLocaleDateString('pt-BR') + '</span></div><span style="background:var(--primary);color:#fff;padding:4px 12px;border-radius:6px;font-size:.8rem">Processando</span>';
          campaignsData.appendChild(newCampaign);
        }
        
        alert('Campanha "' + nome + '" criada com sucesso!\\n\\nO sistema de orquestração MaestroIA irá processar sua campanha automaticamente.');
        // Clear form
        document.getElementById('campaign-form').reset();
        btn.innerHTML = originalText;
        btn.disabled = false;
      }, 2000);
    }
    
    // Schedule Post
    function schedulePost(e) {
      e.preventDefault();
      const content = document.getElementById('schedule-content').value;
      const date = document.getElementById('schedule-date').value;
      const time = document.getElementById('schedule-time').value;
      const platforms = Array.from(document.querySelectorAll('input[name="platforms"]:checked')).map(c => c.value);
      
      if (!content) {
        alert('Por favor, escreva o conteúdo do post.');
        return;
      }
      
      if (!date || !time) {
        alert('Por favor, selecione data e horário.');
        return;
      }
      
      if (platforms.length === 0) {
        alert('Por favor, selecione pelo menos uma plataforma.');
        return;
      }
      
      const btn = document.querySelector('#schedule-form button[type="submit"]');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Agendando...';
      btn.disabled = true;
      
      setTimeout(() => {
        const dataFormatada = new Date(date).toLocaleDateString('pt-BR');
        alert('Post agendado com sucesso!\\n\\nPlataformas: ' + platforms.join(', ') + '\\nData: ' + dataFormatada + ' às ' + time + '\\n\\nO conteúdo será publicado automaticamente.');
        document.getElementById('schedule-form').reset();
        btn.innerHTML = originalText;
        btn.disabled = false;
      }, 1500);
    }
    
    // Run Research
    function runResearch(e) {
      e.preventDefault();
      const query = document.getElementById('research-query').value;
      const niche = document.getElementById('research-niche').value;
      
      if (!query) {
        alert('Por favor, informe o que você quer pesquisar.');
        return;
      }
      
      const btn = document.querySelector('#research-form button[type="submit"]');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Pesquisando...';
      btn.disabled = true;
      
      const resultDiv = document.getElementById('research-result');
      const contentDiv = document.getElementById('research-content');
      resultDiv.style.display = 'block';
      contentDiv.innerHTML = '<div style="text-align:center;padding:40px"><div class="loading-spinner"></div><p style="margin-top:16px">Agente Pesquisador analisando dados do mercado...</p></div>';
      
      // Simulate AI research
      setTimeout(() => {
        contentDiv.innerHTML = `📊 <strong>Análise de Mercado: ${query}</strong>

<strong>Tendências Identificadas:</strong>
• Crescimento de 23% no interesse pelo tema nos últimos 90 dias
• Pico de engajamento observado entre 18h-21h (horário de Brasília)  
• Melhor dia para publicações: Terça-feira e Quinta-feira
• Volume de buscas: Alto (~12.5K/mês)

<strong>Análise do Nicho${niche ? ' (' + niche + ')' : ''}:</strong>
• Competitividade: Média-Alta
• Oportunidades identificadas em micro-nichos
• Tendência de crescimento para os próximos 6 meses

<strong>Recomendações do Agente:</strong>
• Foque em conteúdo educativo e prático
• Utilize vídeos curtos (Reels/TikTok) para maior alcance
• Hashtags recomendadas: #${query.replace(/\\s+/g, '')} #MarketingDigital #Tendencias
• Considere parcerias com micro-influenciadores do nicho

<strong>Próximos Passos Sugeridos:</strong>
1. Criar calendário editorial baseado nos horários de pico
2. Desenvolver série de conteúdos sobre o tema
3. Monitorar métricas semanalmente`;
        
        btn.innerHTML = originalText;
        btn.disabled = false;
      }, 3000);
    }
    
    // Run Strategy
    function runStrategy(e) {
      e.preventDefault();
      const objetivo = document.getElementById('strategy-objetivo').value;
      const negocio = document.getElementById('strategy-negocio').value;
      const publico = document.getElementById('strategy-publico').value;
      
      if (!objetivo || !negocio || !publico) {
        alert('Por favor, preencha todos os campos.');
        return;
      }
      
      const btn = document.querySelector('#strategy-form button[type="submit"]');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Gerando...';
      btn.disabled = true;
      
      const resultDiv = document.getElementById('strategy-result');
      const contentDiv = document.getElementById('strategy-content');
      resultDiv.style.display = 'block';
      contentDiv.innerHTML = '<div style="text-align:center;padding:40px"><div class="loading-spinner"></div><p style="margin-top:16px">Agente Estrategista desenvolvendo seu plano...</p></div>';
      
      setTimeout(() => {
        const objetivoLabels = {
          'lancamento': 'Lançamento de Produto',
          'branding': 'Construção de Marca',
          'leads': 'Geração de Leads',
          'vendas': 'Aumento de Vendas',
          'engajamento': 'Engajamento de Audiência'
        };
        
        contentDiv.innerHTML = `🎯 <strong>Estratégia de Marketing: ${objetivoLabels[objetivo] || objetivo}</strong>

<strong>Análise do Negócio:</strong>
${negocio}

<strong>Público-Alvo Definido:</strong>
${publico}

<strong>Estratégia Recomendada:</strong>

📌 <strong>Fase 1: Preparação (Semana 1-2)</strong>
• Definir personas detalhadas baseadas no público-alvo
• Criar banco de imagens e assets visuais
• Configurar ferramentas de analytics
• Preparar calendário editorial

📌 <strong>Fase 2: Awareness (Semana 3-4)</strong>
• Conteúdo educativo nas redes sociais
• Posts de autoridade no LinkedIn
• Stories interativos no Instagram
• Email de aquecimento para base

📌 <strong>Fase 3: Engajamento (Semana 5-6)</strong>
• Lives e webinars
• Depoimentos e casos de sucesso
• Conteúdo gerado pelo usuário
• Enquetes e interações

📌 <strong>Fase 4: Conversão (Semana 7+)</strong>
• Campanhas de remarketing
• Ofertas exclusivas
• Email marketing de conversão
• Anúncios segmentados

<strong>Canais Prioritários:</strong>
• Instagram (alcance e engajamento)
• LinkedIn (autoridade B2B)
• Email Marketing (conversão)
• Google Ads (tráfego qualificado)

<strong>KPIs Sugeridos:</strong>
• Alcance: 50K+ impressões/mês
• Engajamento: 4%+ taxa média
• Leads: 200+ qualificados/mês
• Conversão: 3%+ do funil`;
        
        btn.innerHTML = originalText;
        btn.disabled = false;
      }, 3500);
    }
    
    // Run Content Creator
    function runContentCreator(e) {
      e.preventDefault();
      const tipo = document.getElementById('content-tipo').value;
      const tema = document.getElementById('content-tema').value;
      const tom = document.getElementById('content-tom').value;
      const info = document.getElementById('content-info').value;
      
      if (!tipo || !tema) {
        alert('Por favor, selecione o tipo e informe o tema do conteúdo.');
        return;
      }
      
      const btn = document.querySelector('#content-form button[type="submit"]');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Criando...';
      btn.disabled = true;
      
      const resultDiv = document.getElementById('content-result');
      const outputDiv = document.getElementById('content-output');
      resultDiv.style.display = 'block';
      outputDiv.innerHTML = '<div style="text-align:center;padding:40px"><div class="loading-spinner"></div><p style="margin-top:16px">Agente Criador gerando conteúdo...</p></div>';
      
      setTimeout(() => {
        const tipoLabels = {
          'post-instagram': 'Post Instagram',
          'post-linkedin': 'Post LinkedIn',
          'ad-copy': 'Copy de Anúncio',
          'email': 'Email Marketing',
          'blog': 'Artigo de Blog',
          'script': 'Script de Vídeo'
        };
        
        let content = '';
        
        if (tipo === 'post-instagram') {
          content = `✨ ${tema}

Você sabia que pequenas mudanças podem gerar grandes resultados?

${info ? info + '\\n\\n' : ''}Nos últimos meses, ajudamos centenas de negócios a transformarem sua presença digital. E o segredo está nos detalhes:

🎯 Consistência > Perfeição
💡 Valor > Volume  
🤝 Conexão > Promoção

Qual desses pilares você precisa fortalecer?

👇 Comenta aqui e vamos trocar ideias!

.
.
.
#${tema.replace(/\\s+/g, '')} #MarketingDigital #Empreendedorismo #Negócios #Crescimento`;
        } else if (tipo === 'post-linkedin') {
          content = `${tema}: Uma reflexão importante

Nos últimos anos, observei uma mudança significativa no mercado...

${info ? info + '\\n\\n' : ''}A verdade é que os profissionais que se destacam são aqueles que entendem:

1️⃣ A importância de se atualizar constantemente
2️⃣ O valor de construir relacionamentos genuínos
3️⃣ A necessidade de compartilhar conhecimento

O que você tem feito para se manter relevante no seu mercado?

#${tema.replace(/\\s+/g, '')} #Carreira #Desenvolvimento #Networking`;
        } else if (tipo === 'ad-copy') {
          content = `🎯 HEADLINE:
${tema} - A solução que você estava esperando

📝 COPY PRINCIPAL:
Cansado de [problema comum]?

Apresentamos [sua solução] - a maneira mais simples de [benefício principal].

${info ? '✅ ' + info + '\\n' : ''}✅ Resultados comprovados
✅ Suporte especializado
✅ Garantia de satisfação

🔥 CTA:
[Botão] Comece Agora - Grátis por 7 dias

⚡ URGÊNCIA:
Oferta válida apenas esta semana`;
        } else if (tipo === 'email') {
          content = `📧 ASSUNTO: ${tema} - Você não vai querer perder isso

---

Olá [Nome],

Espero que esta mensagem te encontre bem!

Estou entrando em contato porque sei que ${tema.toLowerCase()} é algo importante para você.

${info ? info + '\\n\\n' : ''}Nos últimos [período], temos ajudado [perfil do cliente] a alcançar [resultado].

E quero te dar a oportunidade de fazer o mesmo.

**O que você vai conseguir:**
• [Benefício 1]
• [Benefício 2]  
• [Benefício 3]

[Botão: Quero Saber Mais]

Qualquer dúvida, é só responder este email.

Um abraço,
[Seu Nome]

P.S.: Esta oferta é válida apenas até [data].`;
        } else if (tipo === 'blog') {
          content = `# ${tema}: O Guia Completo para [Ano]

## Introdução

${tema} tem se tornado cada vez mais relevante no cenário atual de negócios. Neste artigo, vamos explorar tudo que você precisa saber para dominar este assunto.

${info ? '> ' + info + '\\n\\n' : ''}## Por Que ${tema} é Importante?

No mundo atual, onde a competição é acirrada, entender ${tema.toLowerCase()} pode ser o diferencial entre o sucesso e a estagnação.

### Os Principais Benefícios:

1. **Aumento de visibilidade** - Mais pessoas conhecerão seu trabalho
2. **Maior credibilidade** - Você se posiciona como autoridade
3. **Melhores resultados** - ROI comprovadamente superior

## Como Implementar

### Passo 1: Planejamento
Antes de começar, defina seus objetivos claramente...

### Passo 2: Execução
Com o plano em mãos, é hora de colocar em prática...

### Passo 3: Análise
Monitore os resultados e faça ajustes...

## Conclusão

${tema} não é mais opcional - é essencial. Comece hoje mesmo a implementar essas estratégias e veja seus resultados decolarem.

**Próximos passos:** [CTA]`;
        } else if (tipo === 'script') {
          content = `🎬 SCRIPT DE VÍDEO: ${tema}

---

📍 HOOK (0-3s)
"Você sabia que ${tema.toLowerCase()} pode mudar completamente seus resultados?"

📍 INTRODUÇÃO (3-15s)
"E aí, pessoal! Hoje eu vou te mostrar [o que o vídeo vai ensinar].
${info ? info : 'Fica até o final porque vai valer muito a pena!'}"

📍 CONTEÚDO PRINCIPAL (15s-2min)

**Ponto 1:**
"Primeiro, vamos falar sobre..."
[Explicação]

**Ponto 2:**  
"Agora, o segundo ponto mais importante..."
[Explicação]

**Ponto 3:**
"E por último, mas não menos importante..."
[Explicação]

📍 CTA (últimos 15s)
"Se esse conteúdo te ajudou, deixa o like e se inscreve no canal!
Me conta nos comentários: qual desses pontos foi mais útil pra você?
Até o próximo vídeo! 🚀"

---
⏱️ Duração estimada: 2-3 minutos`;
        }
        
        outputDiv.textContent = content;
        btn.innerHTML = originalText;
        btn.disabled = false;
      }, 3000);
    }
    
    // Copy content to clipboard
    function copyContent() {
      const content = document.getElementById('content-output');
      if (content) {
        navigator.clipboard.writeText(content.textContent).then(() => {
          alert('Conteúdo copiado para a área de transferência!');
        }).catch(() => {
          // Fallback
          const range = document.createRange();
          range.selectNode(content);
          window.getSelection().removeAllRanges();
          window.getSelection().addRange(range);
          document.execCommand('copy');
          alert('Conteúdo copiado!');
        });
      }
    }
    
    function showRegister() {
      alert('Para criar uma conta completa, acesse a versão desktop da plataforma.');
    }
  </script>
</body>
</html>
    """)
