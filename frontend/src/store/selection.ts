import { defineStore } from "pinia";
import { ref } from "vue";

export type LayerType = "point" | "flyline" | "heat" | "3d";

export const useSelectionStore = defineStore("selection", () => {
  const province = ref<string | null>(null);
  /** 当前联动选中的堆场（表格、轮播、地图飞行等） */
  const yardId = ref<number | null>(null);
  /** 仅地图点位点击时为非空，控制详情抽屉；与 yardId 分离避免轮播/表格自动弹抽屉 */
  const drawerYardId = ref<number | null>(null);
  const layer = ref<LayerType>("point");

  const focusYard = (id: number | null, options?: { openDrawer?: boolean }) => {
    yardId.value = id;
    if (id === null) {
      drawerYardId.value = null;
      return;
    }
    if (options?.openDrawer) {
      drawerYardId.value = id;
    } else {
      drawerYardId.value = null;
    }
  };

  const closeYardDetailDrawer = () => {
    drawerYardId.value = null;
  };

  return { province, yardId, drawerYardId, layer, focusYard, closeYardDetailDrawer };
});
