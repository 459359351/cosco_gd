import api from "./client";

export type SysDictRow = {
  id: number;
  dict_type: string;
  code: string;
  label: string;
  parent_code: string | null;
  sort_order: number;
  enabled: boolean;
  remark: string | null;
};

export type DictTypeMeta = {
  type: string;
  label: string;
  has_parent: boolean;
};

export const sysDictApi = {
  types: () => api.get<DictTypeMeta[]>("/sys-dict/types").then((r) => r.data),

  list: (type: string, parent?: string, enabledOnly = true) =>
    api
      .get<{ type: string; items: SysDictRow[] }>("/sys-dict", {
        params: { type, parent, enabled_only: enabledOnly },
      })
      .then((r) => r.data.items),

  create: (body: Record<string, unknown>) => api.post<SysDictRow>("/sys-dict", body).then((r) => r.data),

  update: (id: number, body: Record<string, unknown>) =>
    api.patch<SysDictRow>(`/sys-dict/${id}`, body).then((r) => r.data),

  delete: (id: number) => api.delete(`/sys-dict/${id}`).then((r) => r.data),
};
