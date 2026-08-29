from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no">

<meta name="theme-color" content="#03040b">
<meta name="description" content="Eat Token • Secure • Smart • Seamless">

<title>Eat Token • Krishna Coder</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    -webkit-tap-highlight-color:transparent;
}

html,body{
    width:100%;
    min-height:100%;
}

body{
    min-height:100vh;
    overflow-x:hidden;
    background:#03040b;
    color:#fff;
    font-family:Inter,Arial,sans-serif;
}

/* ================= BACKGROUND ================= */

body::before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(87,58,255,.24),
            transparent 27%
        ),
        radial-gradient(
            circle at 100% 38%,
            rgba(65,60,255,.18),
            transparent 29%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(166,43,255,.10),
            transparent 35%
        );
    z-index:-3;
}

.bg-orb{
    position:fixed;
    border-radius:50%;
    pointer-events:none;
    filter:blur(1px);
    z-index:-2;
}

.orb-left{
    width:390px;
    height:390px;
    top:-210px;
    left:-120px;
    border:1px solid rgba(96,87,255,.55);
    box-shadow:
        0 0 80px rgba(81,65,255,.22),
        inset 0 0 60px rgba(81,65,255,.12);
}

.orb-right{
    width:430px;
    height:430px;
    top:170px;
    right:-300px;
    border:1px solid rgba(91,70,255,.42);
    box-shadow:
        0 0 100px rgba(77,62,255,.18),
        inset 0 0 80px rgba(77,62,255,.08);
}

.noise{
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:-1;
    opacity:.025;
    background-image:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.8'/%3E%3C/svg%3E");
}

/* ================= MAIN ================= */

.container{
    width:100%;
    max-width:900px;
    margin:auto;
    padding:45px 22px 32px;
}

/* ================= BRAND ================= */

.brand{
    text-align:center;
}

.logo{
    width:92px;
    height:92px;
    margin:0 auto 25px;
    border-radius:50%;

    display:flex;
    align-items:center;
    justify-content:center;

    font-size:35px;
    font-weight:700;
    letter-spacing:-3px;

    background:
        linear-gradient(
            145deg,
            #c76cff,
            #765cff 45%,
            #35d7ff
        );

    color:transparent;
    -webkit-background-clip:text;
    background-clip:text;

    border:1px solid rgba(145,112,255,.65);

    box-shadow:
        0 0 35px rgba(111,76,255,.25),
        inset 0 0 25px rgba(255,255,255,.04);

    position:relative;
}

.logo::before{
    content:"";
    position:absolute;
    inset:-1px;
    border-radius:50%;
    border:1px solid rgba(88,184,255,.35);
}

.logo::after{
    content:"✦";
    position:absolute;
    right:-3px;
    top:0;
    font-size:14px;
    color:#fff;
    text-shadow:0 0 15px #fff;
}

.brand h1{
    font-size:46px;
    font-weight:600;
    letter-spacing:10px;
    margin-left:10px;
}

.brand-sub{
    margin-top:14px;
    color:#a39fc9;
    font-size:15px;
    letter-spacing:6px;
}

.gradient-line{
    width:115px;
    height:3px;
    margin:26px auto 28px;
    border-radius:10px;
    background:linear-gradient(
        90deg,
        transparent,
        #d35cff,
        #40bfff,
        transparent
    );
    box-shadow:
        0 0 14px rgba(128,83,255,.8);
}

/* ================= STATUS ================= */

.status{
    width:max-content;
    margin:0 auto 32px;

    display:flex;
    align-items:center;
    gap:12px;

    padding:10px 19px;
    border-radius:30px;

    background:rgba(12,14,32,.58);
    border:1px solid rgba(111,100,220,.25);

    color:#d1cde3;
    font-size:13px;
    letter-spacing:.4px;

    box-shadow:
        0 0 25px rgba(55,45,150,.12),
        inset 0 1px rgba(255,255,255,.04);
}

.status-dot{
    width:10px;
    height:10px;
    border-radius:50%;
    background:#39e982;
    box-shadow:
        0 0 8px #39e982,
        0 0 18px rgba(57,233,130,.7);
}

/* ================= LOGIN CARD ================= */

.card{
    max-width:730px;
    margin:auto;
    padding:38px 50px 40px;

    border-radius:34px;

    background:
        linear-gradient(
            145deg,
            rgba(14,16,38,.80),
            rgba(7,9,22,.73)
        );

    border:1px solid rgba(119,107,218,.42);

    box-shadow:
        0 35px 100px rgba(0,0,0,.42),
        0 0 70px rgba(67,50,180,.08),
        inset 0 1px 0 rgba(255,255,255,.05);

    backdrop-filter:blur(25px);
    -webkit-backdrop-filter:blur(25px);
}

.security-icon{
    width:88px;
    height:88px;
    margin:0 auto 20px;

    display:flex;
    align-items:center;
    justify-content:center;

    font-size:40px;

    color:#73bfff;

    border:2px solid transparent;
    border-radius:25px;

    background:
        linear-gradient(#11142e,#11142e) padding-box,
        linear-gradient(
            145deg,
            #d75cff,
            #5c8dff,
            #25dfff
        ) border-box;

    box-shadow:
        0 0 35px rgba(120,80,255,.18);
}

.card-title{
    text-align:center;
    font-size:32px;
    font-weight:500;
    letter-spacing:-.8px;
}

.card-subtitle{
    text-align:center;
    color:#aaa6ca;
    margin-top:9px;
    margin-bottom:29px;
    font-size:15px;
}

/* ================= LOGIN BUTTON ================= */

.login-btn{
    width:100%;
    min-height:76px;
    margin-bottom:14px;

    padding:12px 19px;

    display:flex;
    align-items:center;
    gap:18px;

    border-radius:22px;

    background:
        linear-gradient(
            100deg,
            rgba(31,31,72,.74),
            rgba(16,18,44,.62)
        );

    border:1px solid rgba(113,107,187,.30);

    color:#fff;

    cursor:pointer;
    text-align:left;

    position:relative;
    overflow:hidden;

    transition:
        transform .22s ease,
        border-color .22s ease,
        box-shadow .22s ease,
        background .22s ease;
}

.login-btn::before{
    content:"";
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:3px;

    background:linear-gradient(
        180deg,
        #d65cff,
        #5d7dff
    );

    box-shadow:0 0 18px #875cff;
}

.login-btn:hover{
    transform:translateY(-2px);
    border-color:rgba(147,124,255,.62);
    box-shadow:
        0 12px 35px rgba(0,0,0,.25),
        0 0 25px rgba(105,76,255,.10);
}

.login-btn:active{
    transform:scale(.985);
}

.provider-icon{
    width:50px;
    height:50px;
    min-width:50px;

    border-radius:50%;

    display:flex;
    align-items:center;
    justify-content:center;

    background:#161a38;

    border:1px solid rgba(255,255,255,.08);

    font-size:22px;
    font-weight:600;

    box-shadow:
        inset 0 0 15px rgba(255,255,255,.03);
}

.google .provider-icon{
    color:#fff;
    font-weight:700;
}

.facebook .provider-icon{
    color:#4d9cff;
}

.apple .provider-icon{
    color:#fff;
}

.x .provider-icon{
    color:#fff;
}

.vk .provider-icon{
    color:#62aaff;
    font-size:17px;
}

.login-text{
    flex:1;
}

.login-text strong{
    display:block;
    font-size:16px;
    font-weight:500;
}

.login-text span{
    display:block;
    margin-top:5px;
    color:#8885aa;
    font-size:11px;
}

.arrow{
    font-size:28px;
    color:#69668e;
    font-weight:300;
    transition:.2s;
}

.login-btn:hover .arrow{
    color:#bca8ff;
    transform:translateX(3px);
}

/* ================= SECURITY NOTE ================= */

.note{
    margin-top:25px;
    padding:18px 20px;

    display:flex;
    gap:13px;
    align-items:flex-start;

    border-radius:20px;

    background:rgba(27,26,58,.42);
    border:1px solid rgba(111,105,181,.19);

    color:#9693b7;
    font-size:12px;
    line-height:1.6;
}

.note-icon{
    width:27px;
    height:27px;
    min-width:27px;

    display:flex;
    align-items:center;
    justify-content:center;

    border:1px solid #986cff;
    border-radius:50%;

    color:#bd91ff;
}

/* ================= SOCIAL ================= */

.social-card{
    max-width:850px;
    margin:60px auto 0;

    padding:23px 28px;

    border-radius:24px;

    background:rgba(12,14,31,.67);
    border:1px solid rgba(105,99,180,.25);

    display:flex;
    align-items:center;
    gap:22px;

    box-shadow:
        0 20px 60px rgba(0,0,0,.25),
        inset 0 1px rgba(255,255,255,.03);
}

.youtube-box{
    width:55px;
    height:55px;
    min-width:55px;

    border-radius:16px;

    display:flex;
    align-items:center;
    justify-content:center;

    background:#ff1748;

    box-shadow:
        0 0 25px rgba(255,23,72,.22);
}

.youtube-box::after{
    content:"▶";
    font-size:20px;
    color:#fff;
    margin-left:3px;
}

.social-info{
    flex:1;
}

.social-info strong{
    display:block;
    font-size:16px;
    font-weight:500;
}

.social-info span{
    display:block;
    color:#8582a5;
    margin-top:5px;
    font-size:12px;
}

.social-links{
    display:flex;
    gap:9px;
    flex-wrap:wrap;
    justify-content:flex-end;
}

.social-btn{
    text-decoration:none;
    color:#dddafa;

    padding:11px 15px;

    border-radius:14px;

    border:1px solid rgba(113,105,190,.27);
    background:rgba(255,255,255,.035);

    font-size:11px;

    transition:.2s;
}

.social-btn:hover{
    border-color:#896dff;
    background:rgba(120,88,255,.10);
    transform:translateY(-2px);
}

/* ================= FOOTER ================= */

footer{
    text-align:center;
    margin-top:34px;

    color:#67647f;
    font-size:11px;
    letter-spacing:.4px;
}

footer b{
    color:#9284c9;
}

/* ================= RESPONSIVE ================= */

@media(max-width:700px){

    .container{
        padding:32px 14px 25px;
    }

    .brand h1{
        font-size:29px;
        letter-spacing:6px;
    }

    .brand-sub{
        font-size:10px;
        letter-spacing:4px;
    }

    .logo{
        width:78px;
        height:78px;
        font-size:29px;
    }

    .card{
        padding:29px 16px 27px;
        border-radius:27px;
    }

    .security-icon{
        width:74px;
        height:74px;
        font-size:32px;
    }

    .card-title{
        font-size:25px;
    }

    .card-subtitle{
        font-size:12px;
    }

    .login-btn{
        min-height:68px;
        border-radius:19px;
        gap:13px;
        padding:10px 13px;
    }

    .provider-icon{
        width:45px;
        height:45px;
        min-width:45px;
    }

    .login-text strong{
        font-size:14px;
    }

    .login-text span{
        font-size:10px;
    }

    .social-card{
        margin-top:35px;
        padding:18px;
        flex-wrap:wrap;
    }

    .social-info{
        min-width:calc(100% - 80px);
    }

    .social-links{
        width:100%;
        justify-content:center;
    }

    .social-btn{
        flex:1;
        text-align:center;
    }
}

@media(max-width:380px){

    .brand h1{
        font-size:24px;
        letter-spacing:4px;
    }

    .card-title{
        font-size:22px;
    }

    .login-text span{
        display:none;
    }

    .social-btn{
        padding:10px 8px;
        font-size:10px;
    }
}
</style>
</head>

<body>

<div class="bg-orb orb-left"></div>
<div class="bg-orb orb-right"></div>
<div class="noise"></div>

<main class="container">

    <!-- BRAND -->
    <section class="brand">

        <div class="logo">KC</div>

        <h1>CODE CAPTURE</h1>

        <div class="brand-sub">
            Secure · Smart · Seamless
        </div>

        <div class="gradient-line"></div>

    </section>

    <!-- STATUS -->
    <div class="status">
        <span class="status-dot"></span>
        Secure Connection
    </div>

    <!-- LOGIN CARD -->
    <section class="card">

        <div class="security-icon">
            ♙
        </div>

        <h2 class="card-title">
            Choose Login Method
        </h2>

        <p class="card-subtitle">
            Continue with your preferred account
        </p>


        <!-- GOOGLE -->
        <button class="login-btn google"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=8&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                G
            </div>

            <div class="login-text">
                <strong>Continue with Google</strong>
                <span>Sign in securely with Google</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- FACEBOOK -->
        <button class="login-btn facebook"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=3&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                f
            </div>

            <div class="login-text">
                <strong>Continue with Facebook</strong>
                <span>Sign in securely with Facebook</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- APPLE -->
        <button class="login-btn apple"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=10&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                ●
            </div>

            <div class="login-text">
                <strong>Continue with Apple</strong>
                <span>Sign in securely with Apple</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- X -->
        <button class="login-btn x"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=11&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                𝕏
            </div>

            <div class="login-text">
                <strong>Continue with X</strong>
                <span>Sign in securely with X</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- VK -->
        <button class="login-btn vk"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=5&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                VK
            </div>

            <div class="login-text">
                <strong>Continue with VK</strong>
                <span>Sign in securely with VK</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- SECURITY -->
        <div class="note">

            <div class="note-icon">
                i
            </div>

            <div>
                Your authentication is handled by the
                respective provider. We do not store your
                password or sensitive information.
            </div>

        </div>

    </section>


    <!-- YOUTUBE / SOCIAL -->
    <section class="social-card">

        <div class="youtube-box"></div>

        <div class="social-info">
            <strong>Code Token Capture?</strong>
            <span>
                Subscribe to our YouTube channel for latest updates
            </span>
        </div>

        <div class="social-links">

            <a class="social-btn"
               href="https://www.youtube.com/@KrishnaCoderOfficial"
               target="_blank"
               rel="noopener noreferrer">
                YouTube →
            </a>

            <a class="social-btn"
               href="https://instagram.com/KrishnaCoderOfficial"
               target="_blank"
               rel="noopener noreferrer">
                Instagram →
            </a>

            <a class="social-btn"
               href="https://t.me/FREEFlRECODE"
               target="_blank"
               rel="noopener noreferrer">
                Telegram →
            </a>

        </div>

    </section>


    <!-- FOOTER -->
    <footer>
        © 2026 Eat Token · Made with
        <b>♥ by Krishna Coder</b>
    </footer>

</main>


<script>

function openLink(url){

    window.open(
        url,
        "_blank",
        "noopener,noreferrer"
    );

}

</script>
</body>
</html>"""    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5056, debug=False)
