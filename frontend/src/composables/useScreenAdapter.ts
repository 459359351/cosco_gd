import { onMounted, onUnmounted, ref } from "vue";

const DESIGN_WIDTH = 1920;
const DESIGN_HEIGHT = 1080;

export function useScreenAdapter() {
  const scale = ref(1);

  const updateScale = () => {
    const wScale = window.innerWidth / DESIGN_WIDTH;
    const hScale = window.innerHeight / DESIGN_HEIGHT;
    scale.value = Math.min(wScale, hScale);
  };

  onMounted(() => {
    updateScale();
    window.addEventListener("resize", updateScale);
  });

  onUnmounted(() => {
    window.removeEventListener("resize", updateScale);
  });

  return { scale };
}
