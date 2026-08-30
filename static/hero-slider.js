document.addEventListener("DOMContentLoaded", () => {

    const slides =
        Array.from(
            document.querySelectorAll(".hero-slide")
        );

    const indicators =
        Array.from(
            document.querySelectorAll(".hero-indicator")
        );


    if (slides.length === 0) {
        return;
    }


    /*
     * MedSecure screensaver timing
     *
     * 4 images × 5 seconds
     * = 20 second complete rotation.
     */

    const SLIDE_DURATION = 5000;


    let currentSlide = 0;
    let sliderTimer = null;



    function showSlide(index) {

        if (
            index < 0 ||
            index >= slides.length
        ) {
            return;
        }


        slides.forEach(
            (slide, slideIndex) => {

                slide.classList.toggle(
                    "hero-slide-active",
                    slideIndex === index
                );

            }
        );


        indicators.forEach(
            (indicator, indicatorIndex) => {

                indicator.classList.toggle(
                    "active",
                    indicatorIndex === index
                );

            }
        );


        currentSlide = index;
    }



    function nextSlide() {

        const nextIndex =
            (currentSlide + 1) % slides.length;

        showSlide(nextIndex);
    }



    function stopSlider() {

        if (sliderTimer !== null) {

            clearInterval(sliderTimer);

            sliderTimer = null;
        }
    }



    function startSlider() {

        stopSlider();

        sliderTimer =
            window.setInterval(
                nextSlide,
                SLIDE_DURATION
            );
    }



    /*
     * Clicking a dot immediately selects that image.
     * It then receives a fresh five-second display period.
     */

    indicators.forEach(
        (indicator, index) => {

            indicator.addEventListener(
                "click",
                () => {

                    showSlide(index);

                    startSlider();

                }
            );

        }
    );



    /*
     * Start on image one.
     */

    showSlide(0);

    if (slides.length > 1) {
        startSlider();
    }



    /*
     * Avoid wasting animation cycles while the browser tab
     * is hidden. Resume when the user returns.
     */

    document.addEventListener(
        "visibilitychange",
        () => {

            if (document.hidden) {

                stopSlider();

            } else {

                startSlider();

            }

        }
    );

});