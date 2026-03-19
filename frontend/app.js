const form = document.querySelector("#user-form");
const nomeInput = document.querySelector("#nome");
const emailInput = document.querySelector("#email");
const feedback = document.querySelector("#feedback");
const userList = document.querySelector("#user-list");
const formTitle = document.querySelector("#form-title");
const submitBtn = document.querySelector("#submit-btn");
const cancelBtn = document.querySelector("#cancel-btn");
const reloadBtn = document.querySelector("#reload-btn");
const searchInput = document.querySelector("#search");
const userCount = document.querySelector("#user-count");

let editingId = null;
let allUsers = [];
const API_BASE = window.location.origin.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:8000";

const clearFeedback = () => {
  feedback.textContent = "";
  feedback.classList.remove("ok", "error");
};

const showFeedback = (message, type = "ok") => {
  feedback.textContent = message;
  feedback.classList.remove("ok", "error");
  feedback.classList.add(type);
};

const resetFormState = () => {
  editingId = null;
  form.reset();
  formTitle.textContent = "Novo usuario";
  submitBtn.textContent = "Salvar";
  cancelBtn.classList.add("hidden");
};

const renderUserItem = (usuario) => {
  const li = document.createElement("li");
  li.className = "user-item";

  const info = document.createElement("div");
  info.innerHTML = `
    <strong>${usuario.nome}</strong>
    <p class="user-meta">#${usuario.id} - ${usuario.email}</p>
  `;

  const actions = document.createElement("div");
  actions.className = "item-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "Editar";
  editBtn.className = "ghost";
  editBtn.addEventListener("click", () => {
    editingId = usuario.id;
    nomeInput.value = usuario.nome;
    emailInput.value = usuario.email;
    formTitle.textContent = `Editando usuario #${usuario.id}`;
    submitBtn.textContent = "Atualizar";
    cancelBtn.classList.remove("hidden");
    clearFeedback();
    nomeInput.focus();
  });

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Excluir";
  deleteBtn.className = "btn-danger";
  deleteBtn.addEventListener("click", async () => {
    const confirmed = window.confirm(`Remover usuario #${usuario.id}?`);
    if (!confirmed) return;

    try {
      const response = await fetch(`${API_BASE}/usuarios/${usuario.id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Falha ao remover usuario.");
      }

      showFeedback("Usuario removido com sucesso.");
      if (editingId === usuario.id) {
        resetFormState();
      }
      await loadUsers();
    } catch (error) {
      showFeedback(error.message, "error");
    }
  });

  actions.append(editBtn, deleteBtn);
  li.append(info, actions);
  return li;
};

const updateList = () => {
  const searchValue = searchInput ? searchInput.value.trim().toLowerCase() : "";
  const filteredUsers = allUsers.filter((usuario) =>
    usuario.nome.toLowerCase().includes(searchValue)
  );
  if (userCount) {
    userCount.textContent = String(filteredUsers.length);
  }
  userList.innerHTML = "";

  if (filteredUsers.length === 0) {
    userList.innerHTML = "<li>Nenhum usuario encontrado.</li>";
    return;
  }

  filteredUsers.forEach((usuario) => {
    userList.appendChild(renderUserItem(usuario));
  });
};

const loadUsers = async () => {
  clearFeedback();
  userList.innerHTML = "<li>Carregando...</li>";

  try {
    const response = await fetch(`${API_BASE}/usuarios`);
    if (!response.ok) {
      throw new Error("Nao foi possivel buscar usuarios.");
    }

    allUsers = await response.json();
    updateList();
  } catch (error) {
    allUsers = [];
    if (userCount) {
      userCount.textContent = "0";
    }
    userList.innerHTML = "<li>Erro ao carregar usuarios.</li>";
    showFeedback(error.message, "error");
  }
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();

  const payload = {
    nome: nomeInput.value.trim(),
    email: emailInput.value.trim(),
  };

  if (!payload.nome || !payload.email) {
    showFeedback("Preencha nome e email.", "error");
    return;
  }

  const isEdit = editingId !== null;
  const url = isEdit
    ? `${API_BASE}/usuarios/${editingId}`
    : `${API_BASE}/usuarios`;
  const method = isEdit ? "PUT" : "POST";

  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Falha na operacao.");
    }

    showFeedback(isEdit ? "Usuario atualizado." : "Usuario criado.");
    resetFormState();
    await loadUsers();
  } catch (error) {
    showFeedback(error.message, "error");
  }
});

cancelBtn.addEventListener("click", () => {
  resetFormState();
  clearFeedback();
});

reloadBtn.addEventListener("click", () => {
  loadUsers();
});

if (searchInput) {
  searchInput.addEventListener("input", () => {
    updateList();
  });
}

loadUsers();
