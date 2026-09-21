document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTOS DA PÁGINA
    // =========================================================

    const modal = document.getElementById("momento-modal");
    const modalOverlay = document.getElementById("momento-modal-overlay");

    const criarBtn = document.getElementById("criar-momento-btn");

    const fecharBtn = document.getElementById("fechar-momento-modal");
    const cancelarBtn = document.getElementById("cancelar-momento-btn");

    const form = document.getElementById("momento-form");

    const momentoEmpty = document.getElementById("momento-empty");
    const momentoCard = document.getElementById("momento-card");

    const momentoSentindo = document.getElementById("momento-sentindo");
    const momentoOuvindo = document.getElementById("momento-ouvindo");
    const momentoLendo = document.getElementById("momento-lendo");
    const momentoPensamento = document.getElementById("momento-pensamento");
    const momentoAtmosfera = document.getElementById("momento-atmosfera");
    const momentoTimestamp = document.getElementById("momento-timestamp");

    const artistaInput = document.getElementById("momento-artista");
    const livroInput = document.getElementById("momento-livro");
    const fraseInput = document.getElementById("momento-frase");
    const pensamentoInput = document.getElementById("momento-pensamento-input");
    const atmosferaInput = document.getElementById("momento-atmosfera-input");

    const characterCount = document.getElementById("momento-character-count");
    const formMessage = document.getElementById("momento-form-message");
    const toast = document.getElementById("momento-toast");


    // =========================================================
    // ABRIR MODAL
    // =========================================================

    function abrirModal() {

        if (!modal) {
            return;
        }

        modal.classList.add("active");
        modal.setAttribute("aria-hidden", "false");

        if (artistaInput) {
            artistaInput.focus();
        }
    }


    // =========================================================
    // FECHAR MODAL
    // =========================================================

    function fecharModal() {

        if (!modal) {
            return;
        }

        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");

        limparMensagem();
    }


    // =========================================================
    // BOTÃO "CRIAR MEU MOMENTO"
    // =========================================================

    if (criarBtn) {

        criarBtn.addEventListener("click", function () {

            limparFormulario();
            abrirModal();

        });

    }



    // =========================================================
    // BOTÃO "FECHAR"
    // =========================================================

    if (fecharBtn) {

        fecharBtn.addEventListener("click", function () {

            fecharModal();

        });

    }


    // =========================================================
    // BOTÃO "CANCELAR"
    // =========================================================

    if (cancelarBtn) {

        cancelarBtn.addEventListener("click", function () {

            fecharModal();

        });

    }


    // =========================================================
    // CLICAR FORA DO MODAL
    // =========================================================

    if (modalOverlay) {

        modalOverlay.addEventListener("click", function () {

            fecharModal();

        });

    }


    // =========================================================
    // TECLA ESC
    // =========================================================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            fecharModal();

        }

    });


    // =========================================================
    // CONTADOR DE CARACTERES
    // =========================================================

    if (pensamentoInput && characterCount) {

        pensamentoInput.addEventListener("input", function () {

            characterCount.textContent =
                pensamentoInput.value.length;

        });

    }


    // =========================================================
    // ENVIO DO FORMULÁRIO
    // =========================================================

    if (form) {

        form.addEventListener("submit", function (event) {

            event.preventDefault();

            limparMensagem();

            // ---------------------------------------------
            // VALORES DOS CAMPOS
            // ---------------------------------------------

            const artista = artistaInput.value.trim();
            const livro = livroInput.value.trim();
            const frase = fraseInput.value;
            const pensamento = pensamentoInput.value.trim();
            const atmosfera = atmosferaInput.value;


            // ---------------------------------------------
            // VALIDAÇÕES
            // ---------------------------------------------

            if (!artista) {

                mostrarMensagem(
                    "Informe o que você está ouvindo."
                );

                artistaInput.focus();

                return;
            }


            if (artista.length > 150) {

                mostrarMensagem(
                    "O nome do artista deve ter no máximo 150 caracteres."
                );

                artistaInput.focus();

                return;
            }


            if (!frase) {

                mostrarMensagem(
                    "Escolha uma forma de começar seu pensamento."
                );

                fraseInput.focus();

                return;
            }


            if (pensamento.length > 160) {

                mostrarMensagem(
                    "O pensamento deve ter no máximo 160 caracteres."
                );

                pensamentoInput.focus();

                return;
            }


            if (!atmosfera) {

                mostrarMensagem(
                    "Escolha uma atmosfera."
                );

                atmosferaInput.focus();

                return;
            }


            // ---------------------------------------------
            // CONVERSÃO DOS VALORES
            // ---------------------------------------------

            const fraseInicio = converterFrase(frase);
            const atmosferaNome = converterAtmosfera(atmosfera);


            // ---------------------------------------------
            // FORMDATA
            //
            // NÃO estamos usando JSON.
            //
            // Esses são exatamente os nomes que
            // a rota Flask /momento espera.
            // ---------------------------------------------

            const dados = new FormData();

            dados.append(
                "ouvindo",
                artista
            );

            dados.append(
                "lendo",
                livro
            );

            dados.append(
                "frase_inicio",
                fraseInicio
            );

            dados.append(
                "frase_complemento",
                pensamento
            );

            dados.append(
                "atmosfera",
                atmosferaNome
            );


            // ---------------------------------------------
            // DESABILITA O BOTÃO DURANTE O ENVIO
            // ---------------------------------------------

            const salvarBtn =
                document.getElementById("salvar-momento-btn");

            if (salvarBtn) {

                salvarBtn.disabled = true;
                salvarBtn.textContent = "Salvando...";

            }


            // ---------------------------------------------
            // ENVIA PARA O FLASK
            // ---------------------------------------------


        fetch("/momento", {
    method: "POST",
    body: dados
})
.then(function (response) {

    console.log("STATUS:", response.status);
    console.log("URL FINAL:", response.url);

    return response.text();

})
.then(function (texto) {

    console.log("RESPOSTA DO FLASK:", texto);

    mostrarToast("✦ Seu momento foi salvo.");

    setTimeout(function () {
    window.location.href = "/profile";
    }, 1000);
})
.catch(function (error) {

    console.error("Erro ao salvar momento:", error);

    mostrarMensagem(
        "Não foi possível salvar seu momento. Tente novamente."
    );

    if (salvarBtn) {
        salvarBtn.disabled = false;
        salvarBtn.textContent = "✦ Salvar momento";
    }

});
        });

    }
    // =========================================================
    // CONVERTER FRASE
    // =========================================================

    function converterFrase(valor) {

        const frases = {

            "minha-mente":
                "Minha mente está em...",

            "ultimamente":
                "Ultimamente tenho pensado em...",

            "ultimamente-pensado":
                "Ultimamente tenho pensado em...",

            "meu-coracao":
                "Meu coração está voltado para...",

            "tentando-entender":
                "Estou tentando entender...",

            "aprendendo":
                "Estou aprendendo sobre...",

            "nao-consigo-parar":
                "Não consigo parar de pensar em...",

            "neste-momento":
                "Neste momento, quero...",

            "tenho-vontade":
                "Tenho vontade de..."

        };


        return frases[valor] || valor;

    }


    // =========================================================
    // CONVERTER ATMOSFERA
    // =========================================================

    function converterAtmosfera(valor) {

        const atmosferas = {

            "noite-tranquila":
                "Noite tranquila",

            "dia-acolhedor":
                "Dia aconchegante",

            "dia-introspectivo":
                "Dia introspectivo",

            "momento-especial":
                "Momento especial",

            "em-paz":
                "Em paz",

            "cheio-de-energia":
                "Cheio de energia"

        };


        return atmosferas[valor] || valor;

    }


    // =========================================================
    // PREENCHER FORMULÁRIO AO EDITAR
    // =========================================================

   function preencherFormularioComMomentoAtual() {

    // Ouvindo
    if (momentoOuvindo && artistaInput) {

        artistaInput.value =
            momentoOuvindo.textContent.trim();

    }


    // Lendo
    if (momentoLendo && livroInput) {

        const livro =
            momentoLendo.textContent.trim();

        if (livro !== "Não estou lendo nada no momento") {

            livroInput.value = livro;

        } else {

            livroInput.value = "";

        }

    }


    // Frase + pensamento
    if (momentoPensamento) {

        const texto =
            momentoPensamento.textContent.trim();

        const frases = [
            "Minha mente está em...",
            "Ultimamente tenho pensado em...",
            "Meu coração está voltado para...",
            "Estou tentando entender...",
            "Estou aprendendo sobre...",
            "Não consigo parar de pensar em...",
            "Neste momento, quero...",
            "Tenho vontade de..."
        ];

        let fraseEncontrada = "";

        for (const frase of frases) {

            if (texto.startsWith(frase)) {

                fraseEncontrada = frase;
                break;

            }

        }

        if (fraseInput && fraseEncontrada) {

            fraseInput.value = fraseEncontrada;

        }

        if (pensamentoInput) {

            pensamentoInput.value =
                texto
                .replace(fraseEncontrada, "")
                .trim();

        }

    }


    // Atmosfera
    if (momentoAtmosfera && atmosferaInput) {

        const atmosfera =
            momentoAtmosfera.textContent.trim();

        const atmosferas = {

            "Noite tranquila": "noite-tranquila",
            "Dia aconchegante": "dia-acolhedor",
            "Dia introspectivo": "dia-introspectivo",
            "Momento especial": "momento-especial",
            "Em paz": "em-paz",
            "Cheio de energia": "cheio-de-energia"

        };

        if (atmosferas[atmosfera]) {

            atmosferaInput.value =
                atmosferas[atmosfera];

        }

    }


    atualizarContador();

}

    // =========================================================
    // LIMPAR FORMULÁRIO
    // =========================================================

    function limparFormulario() {

        if (artistaInput) {
            artistaInput.value = "";
        }

        if (livroInput) {
            livroInput.value = "";
        }

        if (fraseInput) {
            fraseInput.value = "";
        }

        if (pensamentoInput) {
            pensamentoInput.value = "";
        }

        if (atmosferaInput) {
            atmosferaInput.value = "";
        }

        atualizarContador();
        limparMensagem();

    }


    // =========================================================
    // ATUALIZAR CONTADOR
    // =========================================================

    function atualizarContador() {

        if (
            pensamentoInput &&
            characterCount
        ) {

            characterCount.textContent =
                pensamentoInput.value.length;

        }

    }


    // =========================================================
    // MENSAGEM DO FORMULÁRIO
    // =========================================================

    function mostrarMensagem(mensagem) {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = mensagem;

        formMessage.classList.add("show");

    }


    function limparMensagem() {

        if (!formMessage) {
            return;
        }

        formMessage.textContent = "";

        formMessage.classList.remove("show");

    }


    // =========================================================
    // TOAST
    // =========================================================

    function mostrarToast(mensagem) {

        if (!toast) {
            return;
        }

        toast.textContent = mensagem;

        toast.classList.add("show");


        setTimeout(function () {

            toast.classList.remove("show");

        }, 2500);

    }
    // =========================================================
    // ABRIR FORMULÁRIO AO EDITAR PELO PERFIL
    // =========================================================

    const parametros = new URLSearchParams(window.location.search);

    if (parametros.get("editar") === "1") {

        preencherFormularioComMomentoAtual();
        abrirModal();

    }
console.log("MOMENTOS.JS FOI CARREGADO");
});