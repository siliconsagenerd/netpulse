<script setup lang="ts">
import { useI18n } from "../i18n";
const { t } = useI18n();
</script>
<template>
  <div>
    <h1>{{ t("about.title") }}</h1>
    <div class="card"><p>{{ t("about.body") }}</p></div>
  </div>
</template>
