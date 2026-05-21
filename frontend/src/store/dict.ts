import { defineStore } from "pinia";

import { sysDictApi, type SysDictRow } from "@/api/sysDict";

type CacheKey = string;

function cacheKey(type: string, parent?: string) {
  return parent ? `${type}:${parent}` : type;
}

export const useDictStore = defineStore("dict", {
  state: () => ({
    cache: {} as Record<CacheKey, SysDictRow[]>,
    loading: {} as Record<CacheKey, boolean>,
  }),

  getters: {
    provinces(state): SysDictRow[] {
      return state.cache.province ?? [];
    },
  },

  actions: {
    items(type: string, parent?: string): SysDictRow[] {
      return this.cache[cacheKey(type, parent)] ?? [];
    },

    labelOf(type: string, code: string, parent?: string): string {
      const row = this.items(type, parent).find((r) => r.code === code);
      return row?.label ?? code;
    },

    async ensure(type: string, parent?: string, enabledOnly = true): Promise<SysDictRow[]> {
      const key = cacheKey(type, parent);
      if (this.cache[key]?.length) return this.cache[key];
      if (this.loading[key]) {
        await new Promise((r) => setTimeout(r, 50));
        return this.cache[key] ?? [];
      }
      this.loading[key] = true;
      try {
        const items = await sysDictApi.list(type, parent, enabledOnly);
        this.cache[key] = items;
        return items;
      } finally {
        this.loading[key] = false;
      }
    },

    async reload(type: string, parent?: string, enabledOnly = true) {
      const key = cacheKey(type, parent);
      delete this.cache[key];
      return this.ensure(type, parent, enabledOnly);
    },

    async preloadCommon() {
      await Promise.all([
        this.ensure("province"),
        this.ensure("yard_type"),
        this.ensure("yard_status"),
        this.ensure("cargo_category"),
        this.ensure("alert_level"),
        this.ensure("alert_type"),
        this.ensure("vehicle_status"),
      ]);
    },

    citiesOfProvince(provinceCode: string): SysDictRow[] {
      const all = this.cache.city ?? [];
      if (!all.length && provinceCode) {
        return [];
      }
      return all.filter((c) => c.parent_code === provinceCode);
    },

    async ensureCities(provinceCode?: string) {
      const all = await this.ensure("city");
      if (!provinceCode) return all;
      return all.filter((c) => c.parent_code === provinceCode);
    },
  },
});
