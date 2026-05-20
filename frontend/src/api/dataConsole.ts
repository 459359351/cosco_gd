import api from "./client";

export const dataConsole = {
  importHelp: () => api.get("/data-console/import-help").then((r) => r.data),

  yards: (skip = 0, limit = 100) =>
    api.get("/data-console/yards", { params: { skip, limit } }).then((r) => r.data),
  yardCreate: (body: Record<string, unknown>) => api.post("/data-console/yards", body).then((r) => r.data),
  yardUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/yards/${id}`, body).then((r) => r.data),
  yardDelete: (id: number) => api.delete(`/data-console/yards/${id}`).then((r) => r.data),
  yardImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/yards/import", fd).then((r) => r.data);
  },

  flowOd: (skip = 0, limit = 200) =>
    api.get("/data-console/flow-od", { params: { skip, limit } }).then((r) => r.data),
  flowOdCreate: (body: Record<string, unknown>) => api.post("/data-console/flow-od", body).then((r) => r.data),
  flowOdUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/flow-od/${id}`, body).then((r) => r.data),
  flowOdDelete: (id: number) => api.delete(`/data-console/flow-od/${id}`).then((r) => r.data),
  flowOdImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/flow-od/import", fd).then((r) => r.data);
  },

  throughput: (skip = 0, limit = 200) =>
    api.get("/data-console/throughput", { params: { skip, limit } }).then((r) => r.data),
  throughputCreate: (body: Record<string, unknown>) =>
    api.post("/data-console/throughput", body).then((r) => r.data),
  throughputUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/throughput/${id}`, body).then((r) => r.data),
  throughputDelete: (id: number) => api.delete(`/data-console/throughput/${id}`).then((r) => r.data),
  throughputImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/throughput/import", fd).then((r) => r.data);
  },

  cargo: (skip = 0, limit = 200) =>
    api.get("/data-console/cargo", { params: { skip, limit } }).then((r) => r.data),
  cargoCreate: (body: Record<string, unknown>) => api.post("/data-console/cargo", body).then((r) => r.data),
  cargoUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/cargo/${id}`, body).then((r) => r.data),
  cargoDelete: (id: number) => api.delete(`/data-console/cargo/${id}`).then((r) => r.data),
  cargoImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/cargo/import", fd).then((r) => r.data);
  },

  alerts: (skip = 0, limit = 200) =>
    api.get("/data-console/alerts", { params: { skip, limit } }).then((r) => r.data),
  alertCreate: (body: Record<string, unknown>) => api.post("/data-console/alerts", body).then((r) => r.data),
  alertUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/alerts/${id}`, body).then((r) => r.data),
  alertDelete: (id: number) => api.delete(`/data-console/alerts/${id}`).then((r) => r.data),
  alertImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/alerts/import", fd).then((r) => r.data);
  },

  vehicles: (skip = 0, limit = 200) =>
    api.get("/data-console/vehicles", { params: { skip, limit } }).then((r) => r.data),
  vehicleCreate: (body: Record<string, unknown>) =>
    api.post("/data-console/vehicles", body).then((r) => r.data),
  vehicleUpdate: (id: number, body: Record<string, unknown>) =>
    api.patch(`/data-console/vehicles/${id}`, body).then((r) => r.data),
  vehicleDelete: (id: number) => api.delete(`/data-console/vehicles/${id}`).then((r) => r.data),
  vehicleImport: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/data-console/vehicles/import", fd).then((r) => r.data);
  },
};
