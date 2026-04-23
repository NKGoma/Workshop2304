(function () {
  'use strict';

  /* ===== YOUTUBE PLAYER ===== */
  let ytPlayer = null;
  let musicPlaying = false;
  const musicBtn = document.getElementById('music-btn');
  const musicIcon = musicBtn ? musicBtn.querySelector('.music-icon') : null;

  // Called by YouTube IFrame API once it has loaded
  window.onYouTubeIframeAPIReady = function () {
    ytPlayer = new YT.Player('yt-player', {
      videoId: 'TZExMIa9u7Q',
      playerVars: {
        autoplay: 0,
        controls: 0,
        loop: 1,
        playlist: 'TZExMIa9u7Q', // required for loop
        rel: 0,
        modestbranding: 1,
        iv_load_policy: 3,
        fs: 0,
      },
      events: {
        onReady: function () {
          if (musicBtn) musicBtn.disabled = false;
        },
        onStateChange: function (e) {
          // Keep looping if ended
          if (e.data === YT.PlayerState.ENDED && ytPlayer) {
            ytPlayer.playVideo();
          }
        },
      },
    });
  };

  if (musicBtn) {
    musicBtn.disabled = true; // enabled once player is ready

    musicBtn.addEventListener('click', function () {
      if (!ytPlayer || typeof ytPlayer.playVideo !== 'function') return;

      if (musicPlaying) {
        ytPlayer.pauseVideo();
        musicBtn.classList.remove('playing');
        musicBtn.setAttribute('aria-label', 'Play Brazilian background music');
        if (musicIcon) musicIcon.textContent = '🎵';
      } else {
        ytPlayer.playVideo();
        ytPlayer.setVolume(65);
        musicBtn.classList.add('playing');
        musicBtn.setAttribute('aria-label', 'Pause Brazilian background music');
        if (musicIcon) musicIcon.textContent = '🔊';
      }
      musicPlaying = !musicPlaying;
    });
  }

  /* ===== CONFETTI ===== */
  const canvas = document.getElementById('confetti-canvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const CONFETTI_COLORS = ['#009c3b', '#FFDF00', '#002776', '#ffffff', '#FF6B35', '#FF4B8B', '#00C9A7'];
  const particles = [];
  const MAX_PARTICLES = 220;

  function resizeCanvas() {
    if (!canvas) return;
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  if (canvas) {
    window.addEventListener('resize', resizeCanvas, { passive: true });
    resizeCanvas();
  }

  function makeParticle() {
    return {
      x:     Math.random() * (canvas ? canvas.width : window.innerWidth),
      y:     -12,
      w:     5 + Math.random() * 9,
      h:     3 + Math.random() * 5,
      color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
      angle: Math.random() * Math.PI * 2,
      spin:  (Math.random() - 0.5) * 0.18,
      vx:    (Math.random() - 0.5) * 2.5,
      vy:    1.8 + Math.random() * 2.8,
      alpha: 1,
    };
  }

  let frameCount = 0;
  let confettiActive = false;
  let confettiTimer = null;

  function animateConfetti() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    frameCount++;

    if (confettiActive && particles.length < MAX_PARTICLES && frameCount % 2 === 0) {
      particles.push(makeParticle());
      particles.push(makeParticle());
    }

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.angle += p.spin;
      if (p.y > canvas.height * 0.78) p.alpha -= 0.018;
      if (p.alpha <= 0 || p.y > canvas.height + 20) {
        particles.splice(i, 1);
        continue;
      }
      ctx.save();
      ctx.globalAlpha = p.alpha;
      ctx.translate(p.x, p.y);
      ctx.rotate(p.angle);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      ctx.restore();
    }

    requestAnimationFrame(animateConfetti);
  }

  animateConfetti();

  function burstConfetti(seconds) {
    confettiActive = true;
    clearTimeout(confettiTimer);
    confettiTimer = setTimeout(() => { confettiActive = false; }, seconds * 1000);
  }

  /* ===== CTA FORM ===== */
  const rsvpForm = document.getElementById('rsvp-form');
  if (rsvpForm) {
    rsvpForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const nameInput  = this.elements['name'];
      const emailInput = this.elements['email'];
      const name  = nameInput  ? nameInput.value.trim()  : '';
      const email = emailInput ? emailInput.value.trim() : '';

      if (!name) { if (nameInput) nameInput.focus(); return; }
      if (!email || !email.includes('@')) { if (emailInput) emailInput.focus(); return; }

      const safeDiv = document.createElement('div');
      safeDiv.textContent = name;
      const safeName = safeDiv.innerHTML;

      this.innerHTML = `
        <p class="success-msg">
          🎉 Oba! Bem-vindo, ${safeName}!<br>
          Get ready — the fiesta is ON! 🇧🇷🌞
        </p>`;
      burstConfetti(5);
    });
  }

  /* ===== FLOATING EMOJIS ===== */
  const FLOAT_EMOJIS = ['🌞', '🌴', '🌊', '🎉', '🥥', '🎊', '⚽', '🏄', '🎶', '💃', '🕺', '🌺', '🦜', '🍹'];
  const floatLayer = document.getElementById('float-layer');

  function spawnFloat() {
    if (!floatLayer) return;
    const el = document.createElement('span');
    el.className = 'float-emoji';
    el.textContent = FLOAT_EMOJIS[Math.floor(Math.random() * FLOAT_EMOJIS.length)];
    const dur = 5 + Math.random() * 9;
    el.style.cssText = [
      `left:${Math.random() * 94}vw`,
      `font-size:${1.4 + Math.random() * 1.8}rem`,
      `--dur:${dur}s`,
    ].join(';');
    floatLayer.appendChild(el);
    el.addEventListener('animationend', () => el.remove());
  }

  setInterval(spawnFloat, 1100);
  // Seed a few immediately
  for (let i = 0; i < 6; i++) setTimeout(spawnFloat, i * 200);

  /* ===== SCROLL-TRIGGERED ANIMATIONS ===== */
  const scrollObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const idx = parseInt(el.dataset.index || '0', 10) % 50;
      setTimeout(function () {
        el.classList.add('visible');
      }, idx * 80);
      scrollObserver.unobserve(el);
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.activity-card, .section-header, .moment-card').forEach(function (el) {
    scrollObserver.observe(el);
  });

  /* ===== QUOTE CAROUSEL ===== */
  const slides = document.querySelectorAll('.quote-slide');
  const dotsContainer = document.getElementById('carousel-dots');
  let currentSlide = 0;
  let carouselTimer = null;

  if (slides.length && dotsContainer) {
    slides.forEach(function (_, i) {
      const dot = document.createElement('button');
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-label', 'Quote ' + (i + 1));
      if (i === 0) dot.classList.add('active');
      dot.addEventListener('click', function () { goToSlide(i); resetAutoplay(); });
      dotsContainer.appendChild(dot);
    });

    function goToSlide(n) {
      slides[currentSlide].classList.remove('active');
      dotsContainer.children[currentSlide].classList.remove('active');
      currentSlide = (n + slides.length) % slides.length;
      slides[currentSlide].classList.add('active');
      dotsContainer.children[currentSlide].classList.add('active');
    }

    function startAutoplay() {
      carouselTimer = setInterval(function () { goToSlide(currentSlide + 1); }, 4200);
    }

    function resetAutoplay() {
      clearInterval(carouselTimer);
      startAutoplay();
    }

    startAutoplay();

    const carousel = document.getElementById('quote-carousel');
    if (carousel) {
      carousel.addEventListener('mouseenter', function () { clearInterval(carouselTimer); });
      carousel.addEventListener('mouseleave', startAutoplay);
    }
  }

  /* ===== NAVBAR SCROLL EFFECT ===== */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }

})();
