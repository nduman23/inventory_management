const create_account = async (e, elem) => {
  e.preventDefault();
  const [email, username, password1, password2] = Array.from(
    elem.querySelectorAll("input")
  ).map((input) => input.value);
  if (password1 !== password2) {
    show_error("passwords do not match");
    return;
  }
  const body = JSON.stringify({ username, email, password1, password2 });
  const res = await fetch("/signup/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    window.location.href = "/";
  } else {
    show_error(res.message);
  }
};

const login = async (e, elem) => {
  e.preventDefault();
  const [username, password] = Array.from(elem.querySelectorAll("input")).map(
    (input) => input.value
  );

  const body = JSON.stringify({ username, password });
  const res = await fetch("/login/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    window.location.href = "/";
  } else {
    show_error(res.message);
  }
};

const create_store = async (e, elem) => {
  e.preventDefault();
  const name = elem.querySelector("input[name=name]")?.value;

  const body = JSON.stringify({ name });
  const res = await fetch("/create-store/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Store created successfully", () => {
      window.location.href = "/";
    });
  } else {
    show_error(res.message);
  }
};

const create_category = async (e, elem) => {
  e.preventDefault();
  const name = elem.querySelector("input[name=name]")?.value;
  const type = elem.querySelector("select[name=type]")?.value;

  const body = JSON.stringify({ name, type });
  const res = await fetch("/create-category/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Category created successfully", () => {
      window.location.href = "/";
    });
  } else {
    show_error(res.message);
  }
};

const create_router = async (e, elem) => {
  e.preventDefault();
  const snField = elem.querySelector("input[name=serial_number]")
  const category = elem.querySelector("select[name=category]")?.value;
  const serial_number = snField?.value?.trim();
  if (serial_number && serial_number.trim().length != 17) {
    show_error('The serial number is invalid')
    return
  }
  const body = JSON.stringify({ category, serial_number });
  const res = await fetch("/create-router/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success(
      "Router created successfully",
      () => {
        window.location.reload();
      },
      true
    );
  } else {
    show_error(res.message);
  }
};

const edit_router = async (e, elem) => {
  e.preventDefault();
  const { id } = elem.closest(".edit_form.router").dataset;
  const category = elem.querySelector("select[name=category]")?.value;
  const serial_number = elem.querySelector("input[name=serial_number]")?.value;
  const status = elem.querySelector("select[name=status]")?.value;
  const emei = elem.querySelector("input[name=emei]")?.value?.trim();

  const body = JSON.stringify({ id, category, serial_number, emei,status });
  const res = await fetch("/router/", {
    method: "PUT",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Router edited successfully", () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const delete_router = async (id) => {
  const body = JSON.stringify({ id });
  const res = await fetch("/router/", {
    method: "DELETE",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Router deleted successfully", () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const routers_suggestions = async (e, elem) => {
  const { value } = e.target;
  const suggestions_container = elem.nextElementSibling;
  if (value) {
    const res = await fetch(`/routers-suggestions/?value=${value}`).then(
      (res) => res.json()
    );
    if (res.status == 200 && res?.routers.length) {
      const suggestions_container = elem.nextElementSibling;
      suggestions_container.innerHTML = "";
      suggestions_container.classList.add("grid");
      suggestions_container.classList.remove("hidden");
      res.routers.forEach((router) => {
        create_sugestion(suggestions_container, router.emei);
      });
    } else {
      hide_suggestion(suggestions_container);
    }
  } else {
    hide_suggestion(suggestions_container);
  }
};

const categories_suggestions = async (e, elem) => {
  const { value } = e.target;
  const suggestions_container = elem.nextElementSibling;
  if (value) {
    const res = await fetch(`/categories-suggestions/?value=${value}`).then(
      (res) => res.json()
    );
    if (res.status == 200 && res?.categories.length) {
      const suggestions_container = elem.nextElementSibling;
      suggestions_container.innerHTML = "";
      suggestions_container.classList.add("grid");
      suggestions_container.classList.remove("hidden");
      res.categories.forEach((category) => {
        create_sugestion(suggestions_container, category.name);
      });
    } else {
      hide_suggestion(suggestions_container);
    }
  } else {
    hide_suggestion(suggestions_container);
  }
};

const edit_category = async (e, elem) => {
  e.preventDefault();
  const { id } = elem.closest(".edit_form").dataset;
  const type = elem.querySelector("select[name=type]")?.value;
  const name = elem.querySelector("input[name=name]")?.value;

  const body = JSON.stringify({ id, name, type });
  const res = await fetch("/category/", {
    method: "PUT",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Category edited successfully", () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const create_sugestion = (container, content, link = "#") => {
  const suggestion = document.createElement("a");
  suggestion.innerHTML = content;
  suggestion.href = link;
  container.appendChild(suggestion);
};

const hide_suggestion = (suggestions_container) => {
  suggestions_container.innerHTML = "";
  suggestions_container.classList.remove("grid");
  suggestions_container.classList.add("hidden");
};

const toggle_switch_router = (elem) => {
  const form = document.querySelector('.switch_form')
  form.classList.toggle('hidden')
  const router_elem = elem.closest('tr')
  if (router_elem) {
    form.dataset.id = router_elem.dataset.id
  }
}

const open_edit_router = (elem) => {
  const form = document.querySelector(".edit_form.router");
  const container = elem.closest("tr");
  const { id, sn, emei , status ,category } = container.dataset;
  form.dataset.id = id;
  const sn_container = form.querySelector("[name=serial_number]");
  const emei_container = form.querySelector("[name=emei]");
  const category_container = form.querySelector("[name=category]");
  const status_container = form.querySelector("[name=status]");
  sn_container.value = sn;
  emei_container.value = emei;
  const selected_category = Array.from(category_container.options).find(
    (option) => option.value == category
  );

  if (selected_category) {
    selected_category.selected = true;
  }
  const selected_status = Array.from(status_container.options).find(
    (option) => option.value == status
  );

  if (selected_status) {
    selected_status.selected = true;
  }
  form.classList.remove("hidden");
};

const open_edit_category = (elem) => {
  const form = document.querySelector(".edit_form.category");
  const container = elem.closest("tr");
  const { id, name, type } = container.dataset;

  form.dataset.id = id;
  const name_container = form.querySelector("[name=name]");
  const type_container = form.querySelector("[name=type]");
  name_container.value = name;
  const selected_category = Array.from(type_container.options).find(
    (option) => option.value == type
  );
  selected_category.selected = true;
  form.classList.remove("hidden");
};

const delete_category = async (id) => {
  const body = JSON.stringify({ id });
  const res = await fetch("/category/", {
    method: "DELETE",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Category deleted successfully", () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const close_edit_form = (elem) => {
  const form = elem.closest(".edit_form");
  form.classList.add("hidden");
};

const show_user_form = (elem, action) => {
  const form = document.querySelector(".edit_form");
  if (action == "edit") {
    const { id, username, role } = elem.closest(".user_container").dataset;
    form.querySelector("[name=username]").value = username;
    form.querySelector("[name=username]").disabled = true;
    form.querySelector("button").innerHTML = "Edit";
    form.querySelector("h1").innerHTML = "Edit a user";
    const selected_category = Array.from(
      document.querySelector("select").options
    ).find((option) => option.value == role);

    if (selected_category) {
      selected_category.selected = true;
    }
  } else {
    form.querySelector("button").innerHTML = "Edit";
    form.querySelector("h1").innerHTML = "Edit a user";
  }

  form.classList.remove("hidden");
};

const add_user_to_store = async (e, elem) => {
  e.preventDefault();
  const username = elem.querySelector("input[name=username]").value;
  const role = elem.querySelector("select").value;
  const body = JSON.stringify({ username, role });
  const res = await fetch("/profile/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success(res.message, () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const delete_user_from_group = async (elem) => {
  const { id } = elem.closest(".user_container").dataset;
  const body = JSON.stringify({ id });
  const res = await fetch("/profile/", {
    method: "DELETE",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("User deleted successfully", () => {
      window.location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const switch_pages_handler = (e) => {
  const { target } = e;
  if (target.tagName.toLowerCase() != 'span') {
    return
  }
  const name = target.getAttribute("name");

  Array.from(target.parentElement.children).forEach((span) => {
    span == target
      ? span.classList.add("page_active")
      : span.classList.remove("page_active");
  });
  Array.from(document.querySelectorAll("section")).forEach((section) => {
    section.classList.contains(name)
      ? section.classList.remove("hidden")
      : section.classList.add("hidden");
  });
};

const export_routers = async (e) => {
  e.preventDefault();
  const res = await fetch("/router/").then((res) => res.json());
  if (res.status == 200) {
    const routers = res.routers;
    let excel_data = ["id,category,emei,serial_number,created_at"];
    routers.forEach((router) => {
      excel_data.push(
        `${router.id},${router.category__name},${router.emei},${
          router.serial_number
        },${new Date(router.created_at).getDate()}-${
          new Date(router.created_at).getMonth() + 1
        }`
      );
    });
    const now = new Date();
    const name = `Routers-${now.getDate()}-${
      now.getMonth() + 1
    }-${now.getFullYear()}`;
    export_file(excel_data, name);
  } else {
    show_error(res.message);
  }
};

const export_logs = async (e) => {
  e.preventDefault();

  const res = await fetch("/logs-operations").then((res) => res.json());
  if (res.status == 200) {
    const logs = res.logs;
    let excel_data = [
      "username,action,instance,Serial Number,Category Name,Instance Id, Created At",
    ];
    logs.forEach((log) => {
      excel_data.push(
        `${log.user__username},${log.action},${log.instance},${
          log.serial_number ? log.serial_number : ""
        },${log.category_name ? log.category_name : ""},${
          log.instance_id
        },${new Date(log.created_at).getDate()}-${
          new Date(log.created_at).getMonth() + 1
        }`
      );
    });
    const now = new Date();
    const name = `logs-${now.getDate()}-${
      now.getMonth() + 1
    }-${now.getFullYear()}`;
    export_file(excel_data, name);
  } else {
    show_error(res.message);
  }
};

const file_import = async (e) => {
  const file = e.target.files[0];

  file.text().then(async (data) => {
    const routers = data
      .split("\n")
      .slice(3)
      .map((row) => {
        const [id, category, emei, serial_number] = row.split(",");
        return {
          id,
          category,
          emei,
          serial_number,
        };
      });
    const res = await fetch("/router/", {
      method: "POST",
      body: JSON.stringify({ routers }),
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
    }).then((res) => res.json());
    if (res.status == 200) {
      show_success(res.message, () => {
        window.location.reload();
      });
    } else {
      show_error(res.message);
    }
  });
};

const action_change = (elem) => {
  event.preventDefault();
  const action = elem.value;
  Array.from(document.querySelectorAll(".optional")).forEach((elem) => {
    elem.classList.add("hidden");
  });
  Array.from(document.querySelectorAll("." + action)).forEach((elem) => {
    elem.classList.remove("hidden");
  });
};

const submit_action = async (event, elem) => {
  event.preventDefault();
  const orderNumberInput = elem.querySelector('[name=order_number]')
  const sn1 = elem.querySelector('[name=sn1]').value
  const action = elem.querySelector('[name=action]:checked').value
  const order_number = orderNumberInput?.value
  const sn2 = elem.querySelector('[name=sn2]').value
  const return_reason = elem.querySelector('[name=return_reason]').value
  const swap_reason = elem.querySelector('[name=swap_reason]').value
  const comment = elem.querySelector('[name=comment]').value

  const isOrderNumberRequired = isVisible(orderNumberInput)
  if (isOrderNumberRequired) {
    if  (!order_number) {
    show_error('Please type the order number')
    orderNumberInput.focus()
    return
  } else if (order_number && order_number.trim().length != 7) {
    show_error('Please type a valid order number')
    orderNumberInput.focus()
    return
  }
}
  const body = JSON.stringify({
    sn1,
    action,
    order_number,
    sn2,
    return_reason,
    swap_reason,
    comment,
  });
  const res = await fetch("/actions/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status === 200) {
    show_success("Action performed succesfully", () => {
      location.reload();
    });
  } else {
    show_error(res.message);
  }
};

const shipped_change = async(id) => {
  const body = JSON.stringify({id})
  const res = await fetch("/router/", {
    method: "PATCH",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status === 200) {
    show_success(res.message);
  } else {
    show_error(res.message);
  }
};

const toggle_edit_threshold = (elem) => {
  Array.from(elem.parentElement.querySelectorAll('.switch')).forEach(
    elem => elem.classList.toggle('hidden')
  )
}
const change_threshold = async (e) => {
  const {value} = e.target
  const body = JSON.stringify({value})
  const res = await fetch("/profile/", {
    method: "PUT",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status === 200) {
    show_success(res.message,()=> {location.reload()});
  } else {
    show_error(res.message);
  }
}

const bulk_import = (event,elem) => {
  event.preventDefault()
  const {value} = elem
  if (event.inputType == "insertText") {
    if (value && value.includes(' ') || value.includes('\n')) {
      if (isValidSerialNumber(value.trim())) {
        add_router_to_bulk(value.trim())
        elem.value = ''
      }else {
        show_error('Please scan a valid serial number')
        elem.focus()
        return
      }
    }
  }else if(value && event.inputType != "deleteContentBackward") {
    if (isValidSerialNumber(value.trim())) {
      add_router_to_bulk(value.trim())
    }else {
      show_error('Please scan a valid serial number')
      elem.focus()
      return
    }
  }

}

const create_bulk_routers = async(event,elem) => {
  event.preventDefault()
  const serial_numbers = Array.from(document.querySelectorAll('#routers p')).map(elem => elem.dataset.sn)
  const category = elem.querySelector('[name=category]')?.value
  const body = JSON.stringify({ serial_numbers, category });
  const res = await fetch("/bulk-routers/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success(
      "Routers created successfully",
      () => {
        window.location.reload();
      }
    );
  } else {
    show_error(res.message);
  }
}

const add_router_to_bulk = (serial_number) => {
  // <span class="p-2 rounded-sm bg-slate-300 text-gray-500 text-nowrap">dsq-ezad1sq-eza1</span>
  const container = document.querySelector('#routers')
  const p = document.createElement('p')
  const span = document.createElement('span')
  const i = document.createElement('i')
  p.classList.add('p-2','rounded-sm','bg-slate-100','border-2','border-gray-300','text-nowrap','flex','items-center');
  span.innerText = serial_number;
  p.dataset.sn = serial_number
  container.appendChild(p)
  i.classList.add('fa-solid','fa-xmark','text-md','text-red-500','cursor-pointer','p-1','rounded-sm','hover:bg-gray-100','transition-colors')
  i.onclick = () => remove_bulk_router(i)
  p.appendChild(span)
  p.appendChild(i)
}

const remove_bulk_router = (elem) => {
  const parent = elem.closest('p')
  parent.remove()
}

const switch_store = async(event,elem) => {
  event.preventDefault()
  const router_id = elem.closest('.switch_form').dataset.id
  const new_store = elem.querySelector('[name=store]').value
  const body = JSON.stringify({router_id,new_store})  
  const res = await fetch("/switch-store/", {
    method: "POST",
    body,
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  }).then((res) => res.json());
  if (res.status == 200) {
    show_success("Store switched successfully", () => {
      window.location.href = "/";
    });
  } else {
    show_error(res.message);
  }
}