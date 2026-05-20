import api from "@/api/client";

export const getYards = (province?: string) =>
  api.get("/yards", { params: province ? { province } : {} }).then((r) => r.data);
export const getYardDetail = (id: number) => api.get(`/yards/${id}/detail`).then((r) => r.data);
export const getKpiOverview = () => api.get("/kpi/overview").then((r) => r.data);
export const getThroughputTrend = (range = "7d") =>
  api.get("/throughput/trend", { params: { range } }).then((r) => r.data);
export const getCargoDistribution = () => api.get("/cargo/distribution").then((r) => r.data);
export const getYardRanking = (top = 10, province?: string) =>
  api
    .get("/ranking/yards", {
      params: { metric: "teu", top, ...(province ? { province } : {}) },
    })
    .then((r) => r.data);
export const getRecentAlerts = () => api.get("/alerts/recent").then((r) => r.data);
export const getFlowOD = () => api.get("/flow/od").then((r) => r.data);
