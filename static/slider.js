"use strict";

/* =========================================================
   MEDSECURE REAL-TIME HEALTHCARE SLIDER
   Changes image every 3 seconds
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const slider = document.querySelector(".health-slider");

    if (!slider) {
        return;
    }

    const slides = Array.from(
        slider.querySelectorAll(".health-slide")
    );

    const dots = Array.from(
        slider.querySelectorAll(".slider-dot")
    );

    if (slides.length === 0) {
        return;
    }

    let currentIndex = 0;


    /* =====================================================
       SHOW ONE SLIDE
    ===================================================== */

    function displaySlide(index) {

        slides.forEach(function (slide, slideIndex) {

            if (slideIndex === index) {
                slide.classList.add("active");
            } else {
                slide.classList.remove("active");
            }

        });


        dots.forEach(function (dot, dotIndex) {

            if (dotIndex === index) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }

        });

    }


    /* =====================================================
       MOVE TO NEXT SLIDE
    ===================================================== */

    function nextSlide() {

        currentIndex = currentIndex + 1;

        if (currentIndex >= slides.length) {
            currentIndex = 0;
        }

        displaySlide(currentIndex);

    }


    /* =====================================================
       START
    ===================================================== */

    displaySlide(0);


    /*
        3000 milliseconds = 3 seconds

        This is a real browser timer rather than
        relying on CSS animation timing.
    */

    window.setInterval(function () {

        nextSlide();

    }, 3000);

});