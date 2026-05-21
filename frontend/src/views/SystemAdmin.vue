<template>
  <div class="system-admin">
    <header class="top">
      <div>
        <h1>系统管理</h1>
        <p class="sub">维护省份、城市、堆场状态、货种、预警类型、车辆状态等基础字典，驾驶舱与数据管理台将自动引用</p>
      </div>
      <div class="actions">
        <el-button type="primary" link @click="router.push({ name: 'DataConsole' })">数据管理</el-button>
        <el-button type="primary" link @click="router.push('/')">返回驾驶舱</el-button>
      </div>
    </header>

    <el-tabs v-model="activeType" type="border-card" class="tabs" @tab-change="onTypeChange">
      <el-tab-pane v-for="t in dictTypes" :key="t.type" :label="t.label" :name="t.type" />
    </el-tabs>

    <div class="panel">
      <div class="toolbar">
        <el-button type="primary" @click="openAdd">新增</el-button>
        <span class="meta">共 {{ rows.length }} 条</span>
        <el-button text @click="loadRows">刷新</el-button>
      </div>
      <el-table :data="rows" v-loading="loading" stripe border height="58vh">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="code" label="编码" width="140" />
        <el-table-column prop="label" label="显示名" min-width="140" />
        <el-table-column v-if="currentMeta?.has_parent" prop="parent_code" label="上级" width="120" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="enabled" label="启用" width="80">
          <template #default="{ row }">{{ row.enabled ? "是" : "否" }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="delRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dlg"
      class="console-dlg"
      modal-class="console-dlg-overlay"
      :title="editId ? '编辑字典' : '新增字典'"
      width="480px"
      destroy-on-close
    >
      <el-form label-width="100px">
        <el-form-item label="类型">
          <el-input :model-value="currentMeta?.label" disabled />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" :disabled="!!editId" placeholder="唯一编码，如 广东 / normal" />
        </el-form-item>
        <el-form-item label="显示名"><el-input v-model="form.label" /></el-form-item>
        <el-form-item v-if="currentMeta?.has_parent" label="上级">
          <el-select
            v-model="form.parent_code"
            style="width: 100%"
            placeholder="选择省份"
            teleported
            popper-class="console-select-popper"
          >
            <el-option v-for="p in dict.provinces" :key="p.code" :label="p.label" :value="p.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序"><el-input v-model.number="form.sort_order" type="number" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="saveRow">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { sysDictApi, type DictTypeMeta, type SysDictRow } from "@/api/sysDict";
import { useDictStore } from "@/store/dict";

const router = useRouter();
const dict = useDictStore();

const dictTypes = ref<DictTypeMeta[]>([]);
const activeType = ref("province");
const rows = ref<SysDictRow[]>([]);
const loading = ref(false);
const dlg = ref(false);
const editId = ref<number | null>(null);
const form = ref({
  code: "",
  label: "",
  parent_code: "" as string | null,
  sort_order: 0,
  enabled: true,
  remark: "",
});

const currentMeta = computed(() => dictTypes.value.find((t) => t.type === activeType.value));

function err(e: unknown) {
  const x = e as { response?: { data?: { detail?: string } } };
  ElMessage.error(x?.response?.data?.detail || "请求失败");
}

async function loadTypes() {
  dictTypes.value = await sysDictApi.types();
  if (dictTypes.value.length && !dictTypes.value.find((t) => t.type === activeType.value)) {
    activeType.value = dictTypes.value[0].type;
  }
}

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await sysDictApi.list(activeType.value, undefined, false);
  } catch (e) {
    err(e);
  } finally {
    loading.value = false;
  }
}

function onTypeChange() {
  loadRows();
}

function openAdd() {
  editId.value = null;
  form.value = {
    code: "",
    label: "",
    parent_code: currentMeta.value?.has_parent ? "" : null,
    sort_order: rows.value.length + 1,
    enabled: true,
    remark: "",
  };
  dlg.value = true;
}

function openEdit(row: SysDictRow) {
  editId.value = row.id;
  form.value = {
    code: row.code,
    label: row.label,
    parent_code: row.parent_code,
    sort_order: row.sort_order,
    enabled: row.enabled,
    remark: row.remark || "",
  };
  dlg.value = true;
}

async function saveRow() {
  const f = form.value;
  if (!f.code.trim() || !f.label.trim()) {
    ElMessage.warning("请填写编码与显示名");
    return;
  }
  if (currentMeta.value?.has_parent && !f.parent_code) {
    ElMessage.warning("请选择上级省份");
    return;
  }
  try {
    const body = {
      dict_type: activeType.value,
      code: f.code.trim(),
      label: f.label.trim(),
      parent_code: currentMeta.value?.has_parent ? f.parent_code : null,
      sort_order: f.sort_order,
      enabled: f.enabled,
      remark: f.remark || null,
    };
    if (editId.value) {
      await sysDictApi.update(editId.value, {
        label: body.label,
        parent_code: body.parent_code,
        sort_order: body.sort_order,
        enabled: body.enabled,
        remark: body.remark,
      });
    } else {
      await sysDictApi.create(body);
    }
    ElMessage.success("已保存");
    dlg.value = false;
    await dict.reload(activeType.value);
    if (activeType.value === "province") await dict.reload("city");
    await loadRows();
  } catch (e) {
    err(e);
  }
}

async function delRow(row: SysDictRow) {
  try {
    const tip =
      row.dict_type === "province"
        ? `确定删除省份「${row.label}」？将同时删除其下城市字典项。`
        : `确定删除「${row.label}」？`;
    await ElMessageBox.confirm(tip, "确认");
    await sysDictApi.delete(row.id);
    ElMessage.success("已删除");
    await dict.reload(activeType.value);
    if (row.dict_type === "province") await dict.reload("city");
    await loadRows();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

onMounted(async () => {
  try {
    await dict.ensure("province");
    await loadTypes();
    await loadRows();
  } catch (e) {
    err(e);
  }
});
</script>

<style scoped lang="scss">
.system-admin {
  min-height: 100vh;
  padding: 20px 24px 40px;
  background: linear-gradient(180deg, #071325 0%, #0a1e38 100%);
  color: #e8f4ff;
  --el-fill-color-blank: rgba(12, 38, 68, 0.92);
  --el-fill-color-light: rgba(16, 48, 82, 0.88);
  --el-fill-color-lighter: rgba(22, 58, 98, 0.82);
  --el-bg-color: rgba(8, 28, 52, 0.96);
  --el-text-color-primary: #e4f2ff;
  --el-text-color-regular: #c8dff5;
  --el-text-color-secondary: #9ec0e0;
  --el-border-color: rgba(80, 200, 255, 0.32);
  --el-bg-color-overlay: rgba(8, 28, 52, 0.98);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;

  h1 {
    margin: 0 0 8px;
    font-size: 22px;
    color: #8cf0ff;
  }

  .sub {
    margin: 0;
    font-size: 13px;
    color: #b8daf0;
    max-width: 720px;
    line-height: 1.5;
  }

  .actions :deep(.el-button.is-link) {
    color: #7ee0ff;
  }
}

.tabs {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(80, 200, 255, 0.28);
  background: rgba(6, 22, 44, 0.35);

  :deep(.el-tabs__header) {
    margin: 0;
    background: linear-gradient(180deg, rgba(14, 52, 92, 0.98), rgba(8, 34, 62, 0.95));
    border-bottom: 1px solid rgba(80, 200, 255, 0.22);
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }

  :deep(.el-tabs__item) {
    color: #b0d4f0;
    border-color: transparent !important;
    padding: 0 18px;
    height: 42px;
    line-height: 42px;
  }

  :deep(.el-tabs__item:hover) {
    color: #e8f6ff;
  }

  :deep(.el-tabs__item.is-active) {
    color: #5cefff;
    font-weight: 600;
    background: rgba(6, 28, 55, 0.9) !important;
    border: 1px solid rgba(100, 220, 255, 0.35) !important;
    border-bottom-color: transparent !important;
    border-radius: 8px 8px 0 0;
  }

  /* border-card 空内容区默认白底，与数据管理台一致改为深色并收起 */
  :deep(.el-tabs--border-card) {
    background: transparent;
    border: none;
  }

  :deep(.el-tabs--border-card > .el-tabs__content) {
    padding: 0;
    margin: 0;
    min-height: 0;
    height: 0;
    overflow: hidden;
    background: rgba(5, 20, 42, 0.82);
    border-top: none;
  }
}

.panel {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(80, 200, 255, 0.28);
  background: rgba(5, 20, 42, 0.82);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;

  .meta {
    margin-left: auto;
    color: #a8cce8;
    font-size: 13px;
  }

  :deep(.el-button:not(.el-button--primary):not(.is-link)) {
    --el-button-bg-color: rgba(20, 70, 118, 0.75);
    --el-button-border-color: rgba(100, 200, 255, 0.35);
    --el-button-text-color: #e8f4ff;
    --el-button-hover-bg-color: rgba(30, 95, 155, 0.85);
    --el-button-hover-border-color: rgba(120, 220, 255, 0.45);
    --el-button-hover-text-color: #fff;
  }

  :deep(.el-button.is-text) {
    color: #7ee0ff;
  }
}

:deep(.el-table) {
  --el-table-bg-color: rgba(10, 32, 58, 0.55);
  --el-table-tr-bg-color: rgba(10, 32, 58, 0.55);
  --el-table-header-bg-color: rgba(12, 48, 88, 0.95);
  --el-table-row-hover-bg-color: rgba(40, 130, 200, 0.22);
  --el-table-border-color: rgba(70, 190, 255, 0.22);
  --el-table-text-color: #e8f2ff;
  --el-table-header-text-color: #9cf5ff;
  background-color: rgba(8, 26, 48, 0.45);
  color: #e8f2ff;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}

:deep(.el-table__header-wrapper th.el-table__cell) {
  background-color: rgba(12, 48, 88, 0.98) !important;
  color: #9cf5ff !important;
  font-weight: 600;
}

:deep(.el-table__body-wrapper .el-table__body tr > td.el-table__cell) {
  background-color: rgba(10, 36, 64, 0.88) !important;
  color: #e8f2ff !important;
  border-color: rgba(70, 190, 255, 0.18) !important;
}

:deep(.el-table__body-wrapper .el-table__body tr.el-table__row--striped > td.el-table__cell) {
  background-color: rgba(14, 48, 82, 0.88) !important;
}

:deep(.el-table__body-wrapper .el-table__body tr:hover > td.el-table__cell) {
  background-color: rgba(30, 100, 155, 0.38) !important;
}

:deep(.el-table .el-button.is-link.el-button--primary) {
  color: #5ce8ff;
}

:deep(.el-table .el-button.is-link.el-button--danger) {
  color: #ff9aad;
}
</style>
