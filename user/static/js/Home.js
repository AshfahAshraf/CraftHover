document.addEventListener('DOMContentLoaded', () => {

    const contentArea = document.querySelector('.contentArea');
    const jewelryImage = document.querySelector('.jewelry-image');
    const scrollText = document.querySelector('.scroll-text');



    // --- SPLIT TEXT REVEAL ---
    const splitTexts = document.querySelectorAll('.split-reveal');

    splitTexts.forEach(text => {
        const content = text.textContent;
        text.textContent = '';

        [...content].forEach((char, i) => {
            const span = document.createElement('span');
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.classList.add('char');
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


    // --- SVG TEXT SETUP ---
    if (scrollText) {
        scrollText.style.strokeDasharray = "4000";
        scrollText.style.strokeDashoffset = "4000";
    }


    // --- HERO SCROLL ANIMATION ---
    window.addEventListener('scroll', () => {

        window.requestAnimationFrame(() => {

            const scrollY = window.scrollY;

            // increase for more scroll height
            const maxScroll = window.innerHeight * 3;

            const progress = Math.min(scrollY / maxScroll, 1);

            /*
            0.00 - 0.30 image zoom
            0.30 - 0.75 writing + fade image
            0.75 - 1.00 next section
            */


            // IMAGE ZOOM
            const zoomProgress = Math.min(progress / 0.30, 1);

            const blurAmount = zoomProgress * 20;
            const opacityAmount = Math.max(1 - (zoomProgress * 1.2), 0);

            if (contentArea) {
                contentArea.style.filter = `blur(${blurAmount}px)`;
                contentArea.style.opacity = opacityAmount;
            }

            const scaleAmount = 1 + (zoomProgress * 0.7);
            const translateYAmount = zoomProgress * -70;

            if (jewelryImage) {
                jewelryImage.style.transform =
                    `translateY(${translateYAmount}px) scale(${scaleAmount})`;
            }


            // TEXT WRITING
            let textStart = 0.30;
            let textEnd = 0.75;

            let textProgress = Math.min(
                Math.max((progress - textStart) / (textEnd - textStart), 0),
                1
            );

            if (scrollText) {
                const drawProgress = 4000 - (textProgress * 4000);
                scrollText.style.strokeDashoffset = drawProgress;
            }


            // IMAGE FADE
            let fadeStart = 0.30;
            let fadeEnd = 0.75;

            let fadeProgress = Math.min(
                Math.max((progress - fadeStart) / (fadeEnd - fadeStart), 0),
                1
            );

            if (jewelryImage) {
                jewelryImage.style.opacity = 1 - fadeProgress;
            }

        });

    });
    // --- VIDEO REELS ---
    const reelsTrack = document.getElementById('reelsTrack');

    if (reelsTrack) {

        let reelsPos = 0;
        let reelsSpeed = 0.8;
        let reelsPaused = false;

        const animateReels = () => {

            if (!reelsPaused) {
                reelsPos -= reelsSpeed;

                const halfWidth = reelsTrack.scrollWidth / 2;

                if (Math.abs(reelsPos) >= halfWidth) {
                    reelsPos = 0;
                }

                reelsTrack.style.transform =
                    `translateX(${reelsPos}px)`;
            }

            requestAnimationFrame(animateReels);
        };

        animateReels();

        reelsTrack.addEventListener('mouseenter', () => reelsPaused = true);
        reelsTrack.addEventListener('mouseleave', () => reelsPaused = false);
    }



    // --- SCROLL REVEAL ---
    const revealElements = document.querySelectorAll('.scroll-reveal');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {

            if (entry.isIntersecting) {
                entry.target.classList.add('is-active');
            } else {
                entry.target.classList.remove('is-active');
            }

        });
    }, {
        threshold: 0.15
    });

    revealElements.forEach(el => revealObserver.observe(el));

});