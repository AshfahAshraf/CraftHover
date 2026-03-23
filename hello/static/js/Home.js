   
   
   document.addEventListener('DOMContentLoaded', () => {

    const contentArea = document.querySelector('.contentArea');
    const jewelryImage = document.querySelector('.jewelry-image');
    const scrollText = document.querySelector('.scroll-text');

    // --- CUSTOM CURSOR LOGIC ---
    const cursor = document.querySelector('.custom-cursor');
    const dot = document.querySelector('.cursor-dot');

    if (cursor && dot) {
        let mouseX = 0, mouseY = 0;

        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        const animateCursor = () => {
            dot.style.left = `${mouseX}px`;
            dot.style.top = `${mouseY}px`;
            requestAnimationFrame(animateCursor);
        };
        animateCursor();
    }

    // --- SPLIT TEXT REVEAL ---
    const splitTexts = document.querySelectorAll('.split-reveal');
    splitTexts.forEach(text => {
        const content = text.textContent;
        text.textContent = '';
        [...content].forEach((char, i) => {
            const span = document.createElement('span');
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.classList.add('char');
            // Inline delay for perfect stagger
            span.style.transitionDelay = `${i * 0.04}s`;
            text.appendChild(span);
        });
    });

    const textObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            } else {
                entry.target.classList.remove('active');
            }
        });
    }, { threshold: 0.1 });

    splitTexts.forEach(text => textObserver.observe(text));


    // Setup initial SVG stroke state (4000 is long enough to cover huge font contours safely)
    if (scrollText) {
        scrollText.style.strokeDasharray = "4000";
        scrollText.style.strokeDashoffset = "4000";
    }

    window.addEventListener('scroll', () => {
        // Request animation frame for smooth visual updates
        window.requestAnimationFrame(() => {
            const scrollY = window.scrollY;

            // Total scroll height 800vh -> 7x innerHeight
            const maxScroll = window.innerHeight * 7;
            const progress = Math.min(scrollY / maxScroll, 1);

            // Phase timings (Optimized for slower, premium reveal):
            // 0.00 to 0.20 : Image Zooming
            // 0.20 to 0.80 : Text Drawing CRAFTHOVER (60% of range for slow write)
            // 0.80 to 1.00 : Fade IN Clouds + Parallax
            
            // 1. Image Zooming
            const zoomProgress = Math.min(progress / 0.20, 1);
            const blurAmount = zoomProgress * 20;
            const opacityAmount = Math.max(1 - (zoomProgress * 1.5), 0);
            
            if (contentArea) {
                contentArea.style.filter = `blur(${blurAmount}px)`;
                contentArea.style.opacity = opacityAmount;
            }
            
            const scaleAmount = 1 + (zoomProgress * 0.7);
            const translateYAmount = zoomProgress * -70; 
            if (jewelryImage) jewelryImage.style.transform = `translateY(${translateYAmount}px) scale(${scaleAmount})`;
            
            // 2. Text Drawing CRAFTHOVER
            let textProgress = 0;
            if (progress > 0.20) {
                textProgress = Math.min((progress - 0.20) / 0.60, 1);
            }
            if (scrollText) {
                const drawProgress = 4000 - (textProgress * 4000);
                scrollText.style.strokeDashoffset = drawProgress;
            }
            
            // Fade out the jewelry image smoothly during the CRAFTHOVER animation
            if (jewelryImage) {
                jewelryImage.style.opacity = 1 - textProgress;
            }

            // 3. Fading in the Cloud Background section + Scroll Parallax
            let transitionProgress = 0;
            if (progress > 0.80) {
                transitionProgress = Math.min((progress - 0.80) / 0.20, 1);
            }

            const cloudBgArea = document.querySelector('.new-cloud-background');
            const cloudCanvas = document.getElementById('cloudCanvas');

            if (cloudBgArea) {
                cloudBgArea.style.opacity = transitionProgress;
            }

            if (cloudCanvas) {
                // Interactive zoom and pan driven purely by user scroll
                const panX = transitionProgress * -15;
                const panY = transitionProgress * -8;
                const scale1 = 1 + (transitionProgress * 0.3); // slight zoom 1.0 to 1.3

                cloudCanvas.style.transform = `translate(${panX}%, ${panY}%) scale(${scale1})`;
            }

            // --- EXPERIMENTAL: Cinematic Studio Video Reveal (Clip Path Scroll) ---
            const studioReveal = document.querySelector('.studio-reveal');
            const videoClipper = document.getElementById('videoClipper');
            if (studioReveal && videoClipper) {
                const rect = studioReveal.getBoundingClientRect();
                const startScroll = rect.top;
                const totalScroll = rect.height - window.innerHeight;

                if (startScroll <= 0 && startScroll >= -totalScroll) {
                    // We are actively inside the 300vh sticky section
                    const studioProgress = Math.abs(startScroll) / totalScroll;
                    // Circle radius grows from 5% to 150% (to cover corners completely)
                    const circleSize = 5 + (studioProgress * 145);
                    videoClipper.style.clipPath = `circle(${circleSize}% at 50% 50%)`;
                } else if (startScroll > 0) {
                    videoClipper.style.clipPath = `circle(5% at 50% 50%)`;
                } else {
                    videoClipper.style.clipPath = `circle(150% at 50% 50%)`;
                }
            }
        });
    });

    // --- INFINITE MARQUEE ---
    const pmTrack = document.getElementById('pmTrack');
    let pmPos = 0;
    let pmSpeed = 1;
    let pmRafId;

    // Reverse marquee direction based on scroll wheel direction
    let lastScrollY = window.scrollY;
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        if (currentScrollY > lastScrollY) {
            pmSpeed = -1.5; // Scroll down = move left natively
        } else {
            pmSpeed = 1.5;  // Scroll up = move right dynamically!
        }
        lastScrollY = currentScrollY;
    });

    const animateMarquee = () => {
        if (pmTrack) {
            pmPos += pmSpeed;
            // Simple infinite loop using duplicated elements length approach
            // Assumes total width is around 3000px, realistically use a measured width
            if (pmPos < -3000) pmPos = 0;
            if (pmPos > 0) pmPos = -3000;
            pmTrack.style.transform = `translateX(${pmPos}px)`;
        }
        pmRafId = requestAnimationFrame(animateMarquee);
    }
    animateMarquee();

    // --- VIDEO REELS CONTINUOUS MARQUEE ---
    const reelsTrack = document.getElementById('reelsTrack');
    if (reelsTrack) {
        let reelsPos = 0;
        let reelsSpeed = 0.8; // High-end cinematic speed
        let reelsPaused = false;
        let reelsRafId;

        const animateReels = () => {
            if (!reelsPaused) {
                reelsPos -= reelsSpeed;
                
                // We calculate the threshold based on the actual content width 
                // Since we duplicated the items in HTML, we reset when the first half passes.
                const halfWidth = reelsTrack.scrollWidth / 2;
                if (Math.abs(reelsPos) >= halfWidth) {
                    reelsPos = 0;
                }
                reelsTrack.style.transform = `translateX(${reelsPos}px)`;
            }
            reelsRafId = requestAnimationFrame(animateReels);
        };

        animateReels();

        // Pause on Hover for better viewing experience
        reelsTrack.addEventListener('mouseenter', () => reelsPaused = true);
        reelsTrack.addEventListener('mouseleave', () => reelsPaused = false);
    }


    // --- SCROLL REVEAL ANIMATIONS (Every time it scrolls into view) ---
    const revealElements = document.querySelectorAll('.scroll-reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-active');
            } else {
                // Remove class to ensure animation repeatedly triggers when scrolling continuously
                entry.target.classList.remove('is-active');
            }
        });
    }, { root: null, rootMargin: '0px', threshold: 0.15 });

    revealElements.forEach(el => revealObserver.observe(el));

    // --- CANVAS CLOUD ANIMATION ---
    const canvas = document.getElementById('cloudCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width, height;
        const resize = () => {
            width = window.innerWidth * 1.3;
            height = window.innerHeight * 1.3;
            canvas.width = width;
            canvas.height = height;
        };
        window.addEventListener('resize', resize);
        resize();

        class Cloud {
            constructor() { this.reset(true); }
            reset(randomX = false) {
                this.z = Math.random() * 0.8 + 0.2; // depth
                this.x = randomX ? Math.random() * width : -400 * this.z;
                this.y = (Math.random() * height * 0.8) - (height * 0.1);
                this.speed = (Math.random() * 0.4 + 0.1) * this.z;
                this.scale = this.z * (Math.random() * 0.5 + 0.8);
                this.opacity = this.z * 0.6 + 0.1;

                this.puffs = [];
                let numPuffs = Math.floor(Math.random() * 10) + 4; // 4 to 13 puffs
                let cloudWidth = Math.random() * 320 + 80;
                let cloudHeight = Math.random() * 80 + 30;
                for (let i = 0; i < numPuffs; i++) {
                    this.puffs.push({
                        cx: (Math.random() - 0.5) * cloudWidth,
                        cy: (Math.random() - 0.5) * cloudHeight,
                        r: Math.random() * 80 + 40
                    });
                }
            }
            update() {
                this.x += this.speed;
                if (this.x > width + 400) this.reset();
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.scale(this.scale, this.scale);
                ctx.globalAlpha = this.opacity;

                for (let puff of this.puffs) {
                    ctx.beginPath();
                    ctx.arc(puff.cx, puff.cy, puff.r, 0, Math.PI * 2);
                    let grad = ctx.createRadialGradient(puff.cx, puff.cy, 0, puff.cx, puff.cy, puff.r);
                    grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
                    grad.addColorStop(0.4, 'rgba(255, 255, 255, 0.8)');
                    grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.fillStyle = grad;
                    ctx.fill();
                }
                ctx.restore();
            }
        }

        const clouds = [];
        for (let i = 0; i < 35; i++) clouds.push(new Cloud());
        clouds.sort((a, b) => a.z - b.z); // Sort by depth for correct overlapping

        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            for (let cloud of clouds) {
                cloud.update();
                cloud.draw();
            }
            requestAnimationFrame(animate);
        };
        animate();
    }
});




