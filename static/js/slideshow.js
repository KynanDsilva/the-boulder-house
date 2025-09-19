let currentSlide = parseInt(localStorage.getItem("currentSlide")) || 0;
const slides = document.querySelectorAll(".slide");
const dots = document.querySelectorAll(".dot");
let intervalId;

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
    localStorage.setItem("currentSlide", index);
    dots.forEach((dot, i) => dot.classList.toggle("active", i === index));
    currentSlide = index;
}

document.querySelector('.next').addEventListener('click', () => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
    clearInterval(intervalId); // Clear the existing interval
    startInterval(); // Start a new interval
});

document.querySelector('.prev').addEventListener('click', () => {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
    clearInterval(intervalId); // Clear the existing interval
    startInterval(); // Start a new interval
});

function startInterval() {
    intervalId = setInterval(() => {
        let next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }, 10000); // Change the number to adjust the slide interval
}

dots.forEach((dot, i) => {
    dot.addEventListener("click", () => {
        showSlide(i);
        clearInterval(intervalId); // Clear the existing interval
        startInterval(); // Start a new interval
    });
});

// Show the saved slide on load
showSlide(currentSlide);
startInterval(); // Initialize the interval