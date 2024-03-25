const btn_abrilModal = document.querySelector("#mostrarFormulario");
const btn_CerrarModal = document.querySelector("#Enviar");
const modal = document.querySelector("formularioContainer");

btn_abrilModal.addEventListener('click', () => {
    modal.show();
});