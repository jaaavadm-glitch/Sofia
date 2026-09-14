<?php
$JSON_FILE = __DIR__ . '/apps.json';
$apps = json_decode(file_get_contents($JSON_FILE), true) ?: [];
$id = $_GET['id'] ?? '';
$app = null;
foreach ($apps as $a) { if ($a['id'] === $id) { $app = $a; break; } }
if (!$app) { header('Location: index.html'); exit; }
$avatarUrl = !empty($app['avatar']) ? 'avatars/' . $app['avatar'] : '';
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= htmlspecialchars($app['name']) ?> | Sofio</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;800;900&family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --purple:#8b5cf6;--purple-dark:#6d28d9;--blue:#3b82f6;--cyan:#06b6d4;
  --pink:#ec4899;--gold:#fbbf24;--bg:#07071a;--text:#e9e5ff;--text-dim:#8b85b8;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:'Vazirmatn',sans-serif;min-height:100vh;direction:rtl;overflow-x:hidden;}

.glow-bg{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(100px);opacity:.4;animation:float 12s ease-in-out infinite alternate;}
.orb1{width:500px;height:500px;background:var(--purple);top:-18%;left:-12%;}
.orb2{width:420px;height:420px;background:var(--blue);bottom:-15%;right:-10%;animation-delay:2s;}
.orb3{width:350px;height:350px;background:var(--cyan);top:35%;left:40%;animation-delay:4s;opacity:.22;}
.orb4{width:300px;height:300px;background:var(--pink);top:10%;right:12%;animation-delay:6s;opacity:.2;}
@keyframes float{0%{transform:translate(0,0) scale(1);}50%{transform:translate(50px,-45px) scale(1.15);}100%{transform:translate(-30px,35px) scale(.92);}}

.stars{position:fixed;inset:0;pointer-events:none;z-index:0;}
.star{position:absolute;width:2px;height:2px;border-radius:50%;animation:twinkle 3s infinite;}
@keyframes twinkle{0%,100%{opacity:.15;}50%{opacity:.9;box-shadow:0 0 8px currentColor;}}

.wrap{position:relative;z-index:1;max-width:820px;margin:0 auto;padding:28px 22px 80px;}

header{display:flex;justify-content:space-between;align-items:center;margin-bottom:38px;flex-wrap:wrap;gap:14px;}
.logo{
  font-family:'Orbitron',sans-serif;font-size:24px;font-weight:900;letter-spacing:3px;
  color:#fff;text-decoration:none;display:flex;align-items:center;gap:10px;
  text-shadow:0 0 30px rgba(139,92,246,.5);
}
.logo-icon{width:34px;height:34px;filter:drop-shadow(0 0 12px rgba(139,92,246,.8));}
.logo span{background:linear-gradient(120deg,#8b5cf6,#3b82f6,#06b6d4);-webkit-background-clip:text;background-clip:text;color:transparent;}
.back{
  background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.3);
  color:#c4b5fd;padding:10px 22px;border-radius:22px;text-decoration:none;
  font-size:13px;font-weight:700;transition:.35s;display:flex;align-items:center;gap:7px;
}
.back:hover{background:rgba(139,92,246,.25);border-color:var(--purple);color:#fff;box-shadow:0 0 30px rgba(139,92,246,.4);transform:translateX(4px);}
.back svg{width:15px;height:15px;fill:currentColor;}

.hero-card{
  background:rgba(139,92,246,.04);backdrop-filter:blur(18px);
  border:1px solid rgba(139,92,246,.18);border-radius:30px;
  padding:38px;position:relative;overflow:hidden;
  box-shadow:0 25px 80px rgba(0,0,0,.4);
  opacity:0;transform:translateX(80px);
  animation:slideIn .9s cubic-bezier(.16,1,.3,1) forwards;
}
@keyframes slideIn{to{opacity:1;transform:translateX(0);}}
.hero-card::before{
  content:'';position:absolute;inset:0;border-radius:30px;padding:1px;
  background:linear-gradient(135deg,rgba(139,92,246,.6),rgba(59,130,246,.4),rgba(6,182,212,.3),transparent 70%);
  -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
  -webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none;
}

.app-header{display:flex;gap:26px;align-items:center;margin-bottom:30px;flex-wrap:wrap;}

.avatar{
  width:120px;height:120px;border-radius:28px;
  background:linear-gradient(135deg,var(--purple),var(--blue));
  display:flex;align-items:center;justify-content:center;
  font-size:52px;font-weight:900;font-family:'Orbitron';color:#fff;
  flex-shrink:0;overflow:hidden;
  box-shadow:0 12px 50px rgba(139,92,246,.5),0 0 80px rgba(59,130,246,.25);
  position:relative;
  animation:avatarPop .8s cubic-bezier(.34,1.56,.64,1) .3s backwards;
}
@keyframes avatarPop{from{transform:scale(.5) rotate(-15deg);opacity:0;}to{transform:scale(1) rotate(0);opacity:1;}}
.avatar img{width:100%;height:100%;object-fit:cover;}
.avatar::after{content:'';position:absolute;inset:0;background:linear-gradient(135deg,transparent 40%,rgba(255,255,255,.18));pointer-events:none;}

.app-title{flex:1;min-width:220px;}
.app-title h1{
  font-size:32px;font-weight:900;margin-bottom:14px;letter-spacing:.5px;
  background:linear-gradient(120deg,#fff,#a78bfa,#60a5fa,#22d3ee);
  background-size:250% 250%;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  animation:gradientMove 5s ease infinite;
}
@keyframes gradientMove{0%,100%{background-position:0% 50%;}50%{background-position:100% 50%;}}

.tags{display:flex;gap:9px;flex-wrap:wrap;}
.tag{
  background:rgba(139,92,246,.13);border:1px solid rgba(139,92,246,.3);
  color:#c4b5fd;padding:7px 16px;border-radius:14px;
  font-size:13px;font-weight:700;transition:.3s;
  display:flex;align-items:center;gap:6px;
}
.tag:hover{background:rgba(139,92,246,.25);color:#fff;}
.tag.gold{background:rgba(251,191,36,.1);border-color:rgba(251,191,36,.35);color:#fbbf24;box-shadow:0 0 20px rgba(251,191,36,.15);}
.tag.cyan{background:rgba(6,182,212,.1);border-color:rgba(6,182,212,.3);color:#22d3ee;}
.tag svg{width:14px;height:14px;fill:currentColor;}

.desc{
  background:rgba(139,92,246,.04);
  border-right:3px solid var(--purple);
  border-radius:16px;padding:24px 26px;
  line-height:2.1;color:#c8c0e8;font-size:15px;white-space:pre-wrap;
  margin-bottom:30px;font-weight:400;
  position:relative;
}
.desc::before{
  content:'';position:absolute;top:0;right:0;width:60px;height:60px;
  background:radial-gradient(circle at top right,rgba(139,92,246,.15),transparent 70%);
  border-radius:0 16px 0 0;pointer-events:none;
}

.download-btn{
  display:flex;align-items:center;justify-content:center;gap:14px;
  width:100%;
  background:linear-gradient(135deg,var(--purple),var(--blue),var(--cyan));
  background-size:200% 200%;
  color:#fff;padding:22px;border-radius:22px;text-decoration:none;
  font-family:'Vazirmatn',sans-serif;font-weight:900;font-size:18px;
  letter-spacing:.5px;
  box-shadow:0 10px 45px rgba(139,92,246,.5),0 0 70px rgba(59,130,246,.25);
  transition:.4s cubic-bezier(.16,1,.3,1);
  border:none;cursor:pointer;position:relative;overflow:hidden;
  animation:gradientMove 4s ease infinite;
}
.download-btn::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent);
  transform:translateX(-100%);
}
.download-btn:hover::before{animation:shine 1s ease;}
@keyframes shine{to{transform:translateX(100%);}}
.download-btn:hover{
  transform:translateY(-4px) scale(1.02);
  box-shadow:0 15px 60px rgba(139,92,246,.7),0 0 100px rgba(59,130,246,.4);
}
.download-btn svg{width:28px;height:28px;fill:#fff;position:relative;z-index:1;animation:bounceDown 2s infinite;}
@keyframes bounceDown{0%,100%{transform:translateY(0);}50%{transform:translateY(3px);}}
.download-btn span{position:relative;z-index:1;}

footer{
  text-align:center;margin-top:50px;padding-top:30px;
  border-top:1px solid rgba(139,92,246,.12);
  color:var(--text-dim);font-size:13px;
  display:flex;flex-direction:column;align-items:center;gap:12px;
}
.footer-logo{
  font-family:'Orbitron',sans-serif;font-size:20px;font-weight:900;letter-spacing:3px;
  background:linear-gradient(120deg,#8b5cf6,#3b82f6,#06b6d4);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.footer-copy{display:flex;align-items:center;gap:8px;}
.footer-copy svg{width:16px;height:16px;fill:var(--pink);animation:heartbeat 1.5s infinite;}
@keyframes heartbeat{0%,100%{transform:scale(1);}50%{transform:scale(1.25);}}

@media(max-width:640px){
  .app-header{flex-direction:column;text-align:center;}
  .app-title h1{font-size:24px;}
  .hero-card{padding:26px;border-radius:24px;}
  .avatar{width:100px;height:100px;font-size:42px;}
  .download-btn{font-size:15px;padding:18px;flex-direction:column;gap:8px;}
  .download-btn span{font-size:14px;}
}
</style>
</head>
<body>

<div class="glow-bg">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
  <div class="orb orb4"></div>
</div>
<div class="stars" id="stars"></div>

<div class="wrap">
  <header>
    <a href="index.html" class="logo">
      <svg class="logo-icon" viewBox="0 0 24 24">
        <defs>
          <linearGradient id="rocketGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#8b5cf6"/>
            <stop offset="50%" stop-color="#3b82f6"/>
            <stop offset="100%" stop-color="#06b6d4"/>
          </linearGradient>
        </defs>
        <path fill="url(#rocketGrad)" d="M12 2C12 2 6 8 6 14C6 17 8 20 12 23C16 20 18 17 18 14C18 8 12 2 12 2ZM12 11C10.9 11 10 10.1 10 9C10 7.9 10.9 7 12 7C13.1 7 14 7.9 14 9C14 10.1 13.1 11 12 11Z"/>
        <path fill="#fbbf24" d="M4 12L1 15L4 18L7 15L4 12Z" opacity="0.8"/>
        <path fill="#fbbf24" d="M20 12L23 15L20 18L17 15L20 12Z" opacity="0.8"/>
      </svg>
      Sofio<span>.</span>
    </a>
    <a href="index.html" class="back">
      <svg viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
      بازگشت
    </a>
  </header>

  <div class="hero-card">
    <div class="app-header">
      <div class="avatar">
        <?php if ($avatarUrl): ?>
          <img src="<?= htmlspecialchars($avatarUrl) ?>" alt="">
        <?php else: ?>
          <?= htmlspecialchars(mb_substr($app['name'],0,1)) ?>
        <?php endif; ?>
      </div>
      <div class="app-title">
        <h1><?= htmlspecialchars($app['name']) ?></h1>
        <div class="tags">
          <span class="tag gold">
            <svg viewBox="0 0 24 24"><path d="M12 2l2.9 6.9L22 10l-5.5 4.8L18.2 22 12 18.3 5.8 22l1.7-7.2L2 10l7.1-1.1L12 2z"/></svg>
            نسخه <?= htmlspecialchars($app['version']) ?>
          </span>
          <?php if (!empty($app['size'])): ?>
            <span class="tag cyan">
              <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
              <?= htmlspecialchars($app['size']) ?>
            </span>
          <?php endif; ?>
        </div>
      </div>
    </div>

    <?php if (!empty($app['description'])): ?>
      <div class="desc"><?= htmlspecialchars($app['description']) ?></div>
    <?php endif; ?>

    <a href="<?= htmlspecialchars($app['downloadUrl']) ?>" class="download-btn" download>
      <svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
      <span>دانلود <?= htmlspecialchars($app['name']) ?> — نسخه <?= htmlspecialchars($app['version']) ?></span>
    </a>
  </div>

  <footer>
    <div class="footer-logo">SOFIO</div>
    <div class="footer-copy">
      <svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
      <span>Safio 2026</span>
    </div>
  </footer>
</div>

<script>
(function createStars(){
  const stars = document.getElementById('stars');
  const colors = ['#8b5cf6','#3b82f6','#06b6d4','#ec4899','#fbbf24'];
  for(let i=0;i<50;i++){
    const s = document.createElement('div');
    s.className = 'star';
    s.style.left = Math.random()*100+'%';
    s.style.top = Math.random()*100+'%';
    s.style.animationDelay = Math.random()*3+'s';
    s.style.background = colors[Math.floor(Math.random()*colors.length)];
    s.style.color = s.style.background;
    stars.appendChild(s);
  }
})();
</script>

</body>
</html>