import { ref, computed } from "vue";
import de from "./locales/de";
import en from "./locales/en";

const store = { locale: ref(localStorage.getItem("np_lang") || "de") };
const dict = computed(() => (store.locale.value === "de" ? de : en));

export function useI18n() {
  const t = (path: string) => {
    const parts = path.split(".");
    let cur: any = dict.value;
    for (const p of parts) cur = cur?.[p];
    return typeof cur === "string" ? cur : path;
  };
  const setLocale = (l: string) => {
    store.locale.value = l;
    localStorage.setItem("np_lang", l);
  };
  return { locale: store.locale, t, setLocale };
}
