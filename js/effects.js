document.addEventListener("mousemove", (e) => {

    const blur1 =
    document.querySelector(".blur1");

    const blur2 =
    document.querySelector(".blur2");

    let x = e.clientX / window.innerWidth;
    let y = e.clientY / window.innerHeight;

    blur1.style.transform =
    `translate(${x * 40}px, ${y * 40}px)`;

    blur2.style.transform =
    `translate(${-x * 40}px, ${-y * 40}px)`;

});