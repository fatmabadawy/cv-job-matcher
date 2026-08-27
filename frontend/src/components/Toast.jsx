import { useState, useCallback } from "react";

const toasts = [];
let listeners = [];

function notify(listeners) {
  listeners.forEach((fn) => fn([...toasts]));
}

export function addToast(message, type = "info", duration = 3500) {
  const id = Date.now();
  toasts.push({ id, message, type });
  notify(listeners);
  setTimeout(() => {
    const idx = toasts.findIndex((t) => t.id === id);
    if (idx !== -1) { toasts.splice(idx, 1); notify(listeners); }
  }, duration);
}

export function useToasts() {
  const [list, setList] = useState([...toasts]);
  const subscribe = useCallback((fn) => {
    listeners.push(fn);
    return () => { listeners = listeners.filter((l) => l !== fn); };
  }, []);

  useState(() => {
    const unsub = subscribe(setList);
    return unsub;
  });
  return list;
}

export function ToastContainer() {
  const list = useToasts();
  return (
    <div className="toast-container">
      {list.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.message}
        </div>
      ))}
    </div>
  );
}
