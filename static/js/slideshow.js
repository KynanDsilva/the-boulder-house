let currentSlide = parseInt(localStorage.getItem("currentSlide")) || 0;
const slides = document.querySelectorAll(".slide");
const dots = document.querySelectorAll(".dot");
let intervalId;
const totalSlides = slides.length;

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}

document.querySelector('.next').addEventListener('click', () => {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
});

document.querySelector('.prev').addEventListener('click', () => {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    showSlide(currentSlide);
});

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
        dots[i].classList.toggle("active", i === index);
    });
    currentSlide = index;
    localStorage.setItem("currentSlide", currentSlide);
}

function startInterval() {
    intervalId = setInterval(() => {
        let next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }, 10000);
}

// Add click listeners to dots
dots.forEach((dot, i) => {
    dot.addEventListener("click", () => {
        showSlide(i);
        clearInterval(intervalId);
        startInterval();
    });
});

// Show the saved slide on load
showSlide(currentSlide);
startInterval();