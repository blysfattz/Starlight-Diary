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


/* js do humor */

const moodCards = document.querySelectorAll(".mood-card");

const selectedMood = document.getElementById("selectedMood");

const toast = document.getElementById("moodToast");

const toastEmoji = document.getElementById("toastEmoji");

const toastText = document.getElementById("toastText");

const selectedIcon = document.querySelector(".selected-icon");

const moods = {

    feliz:{

        emoji:"😊",

        title:"Feliz",

        message: "Você está irradiando energia positiva hoje!",

        color:"#FFD54F"

    },

    triste:{

        emoji:"😢",

        title:"Triste",

        message:"Tudo bem desacelerar e cuidar de si mesmo..",

        color:"#42A5F5"

    },

    calma:{

        emoji:"😌",

        title:"Calma",

        message:"Paz e equilíbrio guiam o seu dia.",

        color:"#4DD0E1"

    },

    animada:{

        emoji:"🤩",

        title:"Animada",

        message:"Seu entusiasmo é contagiante!",

        color:"#FF5FA2"

    },

    criativa:{

        emoji:"🎨",

        title:"Criativa",

        message:"Sua imaginação está fluindo lindamente.",

        color:"#8E44FF"

    },

    energetico:{

        emoji:"⚡",

        title:"Energético",

        message:"Você está pronto para conquistar qualquer coisa hoje.",

        color:"#FF9800"

    },

    cansado:{

        emoji:"😴",

        title:"Cansado",

        message:"Não se esqueça de recarregar as energias.",

        color:"#90A4AE"

    },

    pensativo:{

        emoji:"🤔",

        title:"Pensativo",

        message:"A reflexão também é uma forma de crescer.",

        color:"#9C6BFF"

    }

};

moodCards.forEach(card=>{

    card.addEventListener("click",()=>{

        moodCards.forEach(item=>{

            item.classList.remove("active");

        });

        card.classList.add("active");

        const mood = card.dataset.mood;

        updateMood(mood);

    });

});

function updateMood(mood){

    const data = moods[mood];

    selectedMood.innerHTML =

        `<strong>${data.emoji} ${data.title}</strong><br>${data.message}`;

    selectedIcon.innerHTML = data.emoji;

    selectedIcon.style.background = data.color;

    updateProfileButton(data.color);

    showToast(data);

    saveMood(mood);

}

function updateProfileButton(color){

    const button = document.querySelector(".edit-profile-btn");

    if(!button) return;

    button.style.background =
        `linear-gradient(135deg, ${color}, #B35EFF)`;

    button.style.boxShadow =
        `0 0 18px ${color}`;

}


function showToast(data){

    toastEmoji.textContent = data.emoji;

    toastText.textContent =
        `Mood updated to ${data.title}`;

    toast.style.borderColor = data.color;

    toast.style.boxShadow =
        `0 0 25px ${data.color}`;

    toast.classList.add("show");

    clearTimeout(window.toastTimeout);

    window.toastTimeout = setTimeout(()=>{

        toast.classList.remove("show");

    },3000);

}

moodCards.forEach(card=>{

    card.addEventListener("mousedown",(event)=>{

        const ripple = document.createElement("span");

        ripple.className = "ripple";

        ripple.style.left =

        event.offsetX + "px";

        ripple.style.top =

        event.offsetY + "px";

        card.appendChild(ripple);

        setTimeout(()=>{

            ripple.remove();

        },600);

    });

});

const observer = new IntersectionObserver(entries=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            entry.target.classList.add("visible");

        }

    });

});

moodCards.forEach(card=>{

    observer.observe(card);

});
function saveMood(mood){
    fetch("/humor", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `tipo=${encodeURIComponent(mood)}`
    })
    .then(response => {
        if(!response.ok){
            throw new Error("Erro ao salvar humor");
        }
        console.log("Humor salvo com sucesso!");
    })
    .catch(err => console.error(err));
}
