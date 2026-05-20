import { defineStore } from "pinia";
import { ref } from "vue";

export const useRealtimeStore = defineStore("realtime", () => {
  const latestEvent = ref<any>(null);
  const connected = ref(false);
  const alertPulseYardId = ref<number | null>(null);

  const applyEvent = (event: any) => {
    latestEvent.value = event;
    if (event?.payload?.yard_id) {
      alertPulseYardId.value = event.payload.yard_id;
    }
  };

  return {
    latestEvent,
    connected,
    alertPulseYardId,
    applyEvent,
  };
});
