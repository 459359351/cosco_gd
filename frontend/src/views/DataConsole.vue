<template>
  <div class="data-console">
    <header class="top">
      <div>
        <h1>PostgreSQL 数据管理台</h1>
        <p class="sub">维护驾驶舱用到的库表：查看明细、单条录入、CSV 批量导入（UTF-8，可用 Excel 另存为 CSV）</p>
      </div>
      <div class="actions">
        <el-button type="primary" link @click="router.push({ name: 'SystemAdmin' })">系统管理</el-button>
        <el-button type="primary" link @click="router.push('/')">返回驾驶舱</el-button>
      </div>
    </header>

    <el-collapse v-if="Object.keys(importHelp).length" class="help">
      <el-collapse-item title="CSV 列说明（点击展开）" name="help">
        <ul>
          <li v-for="(v, k) in importHelp" :key="k"><strong>{{ k }}</strong>：{{ v }}</li>
        </ul>
      </el-collapse-item>
    </el-collapse>

    <el-tabs v-model="active" type="border-card" class="tabs">
      <!-- 堆场 -->
      <el-tab-pane label="堆场 yards" name="yards">
        <div class="toolbar">
          <el-button type="primary" @click="openYardAdd">新增堆场</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="beforeCsv">
            <template #trigger>
              <el-button>导入 CSV</el-button>
            </template>
          </el-upload>
          <span class="meta">共 {{ yardsTotal }} 条</span>
          <el-button text @click="loadYards">刷新</el-button>
        </div>
        <el-table :data="yards" v-loading="yardsLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="code" label="编码" width="120" />
          <el-table-column prop="name" label="名称" min-width="140" />
          <el-table-column prop="province" label="省" width="80" />
          <el-table-column prop="city" label="市" width="90" />
          <el-table-column prop="lng" label="经度" width="100" />
          <el-table-column prop="lat" label="纬度" width="100" />
          <el-table-column prop="capacity" label="容量" width="90" />
          <el-table-column prop="status" label="状态" width="90" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openYardEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delYard(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- OD -->
      <el-tab-pane label="OD 飞线 flow_od" name="flow">
        <div class="toolbar">
          <el-button type="primary" @click="openFlowAdd">新增 OD</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="importFlowCsv">
            <template #trigger><el-button>导入 CSV</el-button></template>
          </el-upload>
          <span class="meta">共 {{ flowTotal }} 条</span>
          <el-button text @click="loadFlow">刷新</el-button>
        </div>
        <el-table :data="flowRows" v-loading="flowLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="from_yard_code" label="起点编码" width="140" />
          <el-table-column prop="to_yard_code" label="终点编码" width="140" />
          <el-table-column prop="value_teu" label="流量" width="100" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openFlowEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delFlow(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 吞吐 -->
      <el-tab-pane label="日吞吐 throughput_daily" name="throughput">
        <div class="toolbar">
          <el-button type="primary" @click="openTpAdd">新增</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="importTpCsv">
            <template #trigger><el-button>导入 CSV</el-button></template>
          </el-upload>
          <span class="meta">共 {{ tpTotal }} 条</span>
          <el-button text @click="loadTp">刷新</el-button>
        </div>
        <el-table :data="tpRows" v-loading="tpLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="yard_id" label="yard_id" width="90" />
          <el-table-column prop="stat_date" label="日期" width="120" />
          <el-table-column prop="in_teu" label="进" width="80" />
          <el-table-column prop="out_teu" label="出" width="80" />
          <el-table-column prop="stock_teu" label="库存" width="90" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openTpEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delTp(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 货种 -->
      <el-tab-pane label="货种 cargo_category" name="cargo">
        <div class="toolbar">
          <el-button type="primary" @click="openCargoAdd">新增</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="importCargoCsv">
            <template #trigger><el-button>导入 CSV</el-button></template>
          </el-upload>
          <span class="meta">共 {{ cargoTotal }} 条</span>
          <el-button text @click="loadCargo">刷新</el-button>
        </div>
        <el-table :data="cargoRows" v-loading="cargoLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="yard_id" label="yard_id" width="90" />
          <el-table-column prop="category" label="货类" width="120" />
          <el-table-column prop="volume" label="货量" width="100" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openCargoEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delCargo(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 预警 -->
      <el-tab-pane label="预警 alerts" name="alerts">
        <div class="toolbar">
          <el-button type="primary" @click="openAlertAdd">新增</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="importAlertCsv">
            <template #trigger><el-button>导入 CSV</el-button></template>
          </el-upload>
          <span class="meta">共 {{ alertTotal }} 条</span>
          <el-button text @click="loadAlerts">刷新</el-button>
        </div>
        <el-table :data="alertRows" v-loading="alertLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="yard_id" label="yard_id" width="80" />
          <el-table-column prop="level" label="级别" width="90" />
          <el-table-column prop="alert_type" label="类型" width="100" />
          <el-table-column prop="message" label="内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="时间" width="180" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openAlertEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delAlert(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 车辆 -->
      <el-tab-pane label="车辆 vehicles" name="vehicles">
        <div class="toolbar">
          <el-button type="primary" @click="openVehAdd">新增</el-button>
          <el-upload :show-file-list="false" accept=".csv,text/csv" :before-upload="importVehCsv">
            <template #trigger><el-button>导入 CSV</el-button></template>
          </el-upload>
          <span class="meta">共 {{ vehTotal }} 条</span>
          <el-button text @click="loadVeh">刷新</el-button>
        </div>
        <el-table :data="vehRows" v-loading="vehLoading" stripe border height="56vh">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="code" label="编号" width="120" />
          <el-table-column prop="from_yard_code" label="起点" width="120" />
          <el-table-column prop="to_yard_code" label="终点" width="120" />
          <el-table-column prop="progress" label="进度" width="80" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openVehEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="delVeh(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 堆场表单 -->
    <el-dialog
      v-model="yardDlg"
      class="console-dlg"
      modal-class="console-dlg-overlay"
      :title="yardEditId ? '编辑堆场' : '新增堆场'"
      width="560px"
      destroy-on-close
      @opened="onYardDlgOpened"
    >
      <el-form label-width="100px">
        <el-form-item label="名称"><el-input v-model="yardForm.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="yardForm.code" :disabled="!!yardEditId" /></el-form-item>
        <el-form-item label="详细地址">
          <div class="addr-row">
            <el-input v-model="yardAddress" placeholder="如：广州市南沙区港前大道南" clearable />
            <el-button type="primary" :loading="geocodeLoading" @click="resolveYardAddress">解析坐标</el-button>
          </div>
        </el-form-item>
        <el-form-item label="类型">
          <el-select
            v-model="yardForm.yard_type"
            style="width: 100%"
            placeholder="选择类型"
            teleported
            popper-class="console-select-popper"
          >
            <el-option v-for="o in dict.items('yard_type')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="省">
          <el-select
            v-model="yardForm.province"
            style="width: 100%"
            placeholder="选择省份"
            teleported
            popper-class="console-select-popper"
            @change="onYardProvinceChange"
          >
            <el-option v-for="o in dict.provinces" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="市">
          <el-select
            v-model="yardForm.city"
            style="width: 100%"
            placeholder="选择城市"
            teleported
            popper-class="console-select-popper"
            :disabled="!yardForm.province"
          >
            <el-option v-for="o in yardCityOptions" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="经度"><el-input v-model.number="yardForm.lng" type="number" step="0.0001" /></el-form-item>
        <el-form-item label="纬度"><el-input v-model.number="yardForm.lat" type="number" step="0.0001" /></el-form-item>
        <el-form-item label="容量"><el-input v-model.number="yardForm.capacity" type="number" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="yardForm.status" style="width: 100%" teleported popper-class="console-select-popper">
            <el-option v-for="o in dict.items('yard_status')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="yardDlg = false">取消</el-button>
        <el-button type="primary" @click="saveYard">保存</el-button>
      </template>
    </el-dialog>

    <!-- OD -->
    <el-dialog v-model="flowDlg" :title="flowEditId ? '编辑 OD' : '新增 OD'" width="480px" destroy-on-close>
      <el-form label-width="110px">
        <el-form-item label="起点编码"><el-input v-model="flowForm.from_yard_code" :disabled="!!flowEditId" /></el-form-item>
        <el-form-item label="终点编码"><el-input v-model="flowForm.to_yard_code" :disabled="!!flowEditId" /></el-form-item>
        <el-form-item label="流量 value_teu"><el-input v-model.number="flowForm.value_teu" type="number" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="flowDlg = false">取消</el-button>
        <el-button type="primary" @click="saveFlow">保存</el-button>
      </template>
    </el-dialog>

    <!-- 吞吐 -->
    <el-dialog v-model="tpDlg" :title="tpEditId ? '编辑吞吐' : '新增吞吐'" width="480px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="yard_id"><el-input v-model.number="tpForm.yard_id" type="number" /></el-form-item>
        <el-form-item label="日期"><el-input v-model="tpForm.stat_date" placeholder="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="进"><el-input v-model.number="tpForm.in_teu" type="number" /></el-form-item>
        <el-form-item label="出"><el-input v-model.number="tpForm.out_teu" type="number" /></el-form-item>
        <el-form-item label="库存"><el-input v-model.number="tpForm.stock_teu" type="number" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tpDlg = false">取消</el-button>
        <el-button type="primary" @click="saveTp">保存</el-button>
      </template>
    </el-dialog>

    <!-- 货种 -->
    <el-dialog v-model="cargoDlg" :title="cargoEditId ? '编辑货种' : '新增货种'" width="440px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="yard_id"><el-input v-model.number="cargoForm.yard_id" type="number" /></el-form-item>
        <el-form-item label="货类">
          <el-select
            v-model="cargoForm.category"
            style="width: 100%"
            filterable
            allow-create
            teleported
            popper-class="console-select-popper"
          >
            <el-option v-for="o in dict.items('cargo_category')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="货量"><el-input v-model.number="cargoForm.volume" type="number" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cargoDlg = false">取消</el-button>
        <el-button type="primary" @click="saveCargo">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预警 -->
    <el-dialog v-model="alertDlg" :title="alertEditId ? '编辑预警' : '新增预警'" width="520px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="yard_id"><el-input v-model.number="alertForm.yard_id" type="number" /></el-form-item>
        <el-form-item label="级别">
          <el-select v-model="alertForm.level" style="width: 100%" teleported popper-class="console-select-popper">
            <el-option v-for="o in dict.items('alert_level')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select
            v-model="alertForm.alert_type"
            style="width: 100%"
            filterable
            allow-create
            teleported
            popper-class="console-select-popper"
          >
            <el-option v-for="o in dict.items('alert_type')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="alertForm.message" type="textarea" rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="alertDlg = false">取消</el-button>
        <el-button type="primary" @click="saveAlert">保存</el-button>
      </template>
    </el-dialog>

    <!-- 车辆 -->
    <el-dialog v-model="vehDlg" :title="vehEditId ? '编辑车辆' : '新增车辆'" width="480px" destroy-on-close>
      <el-form label-width="120px">
        <el-form-item label="编号 code"><el-input v-model="vehForm.code" :disabled="!!vehEditId" /></el-form-item>
        <el-form-item label="起点编码"><el-input v-model="vehForm.from_yard_code" /></el-form-item>
        <el-form-item label="终点编码"><el-input v-model="vehForm.to_yard_code" /></el-form-item>
        <el-form-item label="progress"><el-input v-model.number="vehForm.progress" type="number" step="0.01" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="vehForm.status" style="width: 100%" teleported popper-class="console-select-popper">
            <el-option v-for="o in dict.items('vehicle_status')" :key="o.code" :label="o.label" :value="o.code" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vehDlg = false">取消</el-button>
        <el-button type="primary" @click="saveVeh">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { dataConsole } from "@/api/dataConsole";
import { geocodeAddress } from "@/composables/useGeocoder";
import { useDictStore } from "@/store/dict";

const router = useRouter();
const dict = useDictStore();
const active = ref("yards");
const importHelp = ref<Record<string, string>>({});

watch(active, (n) => {
  if (n === "yards") loadYards();
  if (n === "flow") loadFlow();
  if (n === "throughput") loadTp();
  if (n === "cargo") loadCargo();
  if (n === "alerts") loadAlerts();
  if (n === "vehicles") loadVeh();
});


onMounted(async () => {
  try {
    importHelp.value = (await dataConsole.importHelp()) as Record<string, string>;
  } catch {
    importHelp.value = {};
  }
  try {
    await dict.preloadCommon();
    await dict.ensure("city");
  } catch {
    /* 字典未迁移时仍可手动录入 */
  }
  loadYards();
});

function err(e: unknown) {
  const x = e as { response?: { data?: { detail?: string } }; message?: string };
  ElMessage.error(x?.response?.data?.detail || x?.message || "请求失败");
}

// —— yards ——
const yards = ref<any[]>([]);
const yardsTotal = ref(0);
const yardsLoading = ref(false);
const yardDlg = ref(false);
const yardEditId = ref<number | null>(null);
const yardAddress = ref("");
const geocodeLoading = ref(false);
const yardForm = ref({
  name: "",
  code: "",
  yard_type: "yard",
  province: "",
  city: "",
  lng: 0,
  lat: 0,
  capacity: 0,
  status: "normal",
});

const yardCityOptions = computed(() => dict.citiesOfProvince(yardForm.value.province));

function onYardProvinceChange() {
  yardForm.value.city = "";
}

async function onYardDlgOpened() {
  await dict.preloadCommon();
  await dict.ensure("city");
}

function matchDictCode(type: string, raw: string, parent?: string): string {
  const code = raw.trim();
  if (!code) return "";
  const items = dict.items(type, parent);
  const hit = items.find((r) => r.code === code || r.label === code);
  return hit?.code ?? code;
}

function warnIfNotInDict(type: string, value: string, parent?: string) {
  if (!value) return;
  const items = dict.items(type, parent);
  if (items.length && !items.some((r) => r.code === value)) {
    ElMessage.warning(`「${value}」不在系统字典中，请先在系统管理维护`);
  }
}

async function resolveYardAddress() {
  if (!yardAddress.value.trim()) {
    ElMessage.warning("请先填写详细地址");
    return;
  }
  geocodeLoading.value = true;
  try {
    const r = await geocodeAddress(yardAddress.value, yardForm.value.city || undefined);
    if (!r) return;
    const prov = matchDictCode("province", r.province);
    yardForm.value.province = prov;
    warnIfNotInDict("province", prov);
    const cities = await dict.ensureCities(prov);
    const cityHit = cities.find((c) => c.code === r.city || c.label === r.city);
    yardForm.value.city = cityHit?.code ?? r.city;
    if (!cityHit && r.city) warnIfNotInDict("city", r.city, prov);
    yardForm.value.lng = Number(r.lng.toFixed(6));
    yardForm.value.lat = Number(r.lat.toFixed(6));
    ElMessage.success(r.formattedAddress ? `已解析：${r.formattedAddress}` : "坐标已回填，可继续手动调整");
  } catch (e) {
    err(e);
  } finally {
    geocodeLoading.value = false;
  }
}

async function loadYards() {
  yardsLoading.value = true;
  try {
    const r = await dataConsole.yards(0, 500);
    yards.value = r.items;
    yardsTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    yardsLoading.value = false;
  }
}

function openYardAdd() {
  yardEditId.value = null;
  yardAddress.value = "";
  yardForm.value = {
    name: "",
    code: "",
    yard_type: "yard",
    province: "",
    city: "",
    lng: 0,
    lat: 0,
    capacity: 0,
    status: "normal",
  };
  yardDlg.value = true;
}

function openYardEdit(row: any) {
  yardEditId.value = row.id;
  yardForm.value = { ...row };
  yardAddress.value = `${row.province || ""}${row.city || ""}${row.name || ""}`.trim();
  yardDlg.value = true;
}

async function saveYard() {
  try {
    const f = yardForm.value;
    if (yardEditId.value)
      await dataConsole.yardUpdate(yardEditId.value, {
        name: f.name,
        yard_type: f.yard_type,
        province: f.province,
        city: f.city,
        lng: f.lng,
        lat: f.lat,
        capacity: f.capacity,
        status: f.status,
      });
    else await dataConsole.yardCreate({ ...f });
    ElMessage.success("已保存");
    yardDlg.value = false;
    loadYards();
  } catch (e) {
    err(e);
  }
}

async function delYard(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除堆场 ${row.name}？将级联删除其吞吐/货种/预警记录。`, "确认");
    await dataConsole.yardDelete(row.id);
    ElMessage.success("已删除");
    loadYards();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function beforeCsv(file: File) {
  try {
    const r = await dataConsole.yardImport(file);
    ElMessage.success(`导入完成：新增 ${r.inserted}，更新 ${r.updated}，失败 ${r.errors?.length || 0}`);
    if (r.errors?.length) console.warn(r.errors);
    loadYards();
  } catch (e) {
    err(e);
  }
  return false;
}

// —— flow ——
const flowRows = ref<any[]>([]);
const flowTotal = ref(0);
const flowLoading = ref(false);
const flowDlg = ref(false);
const flowEditId = ref<number | null>(null);
const flowForm = ref({ from_yard_code: "", to_yard_code: "", value_teu: 0 });

async function loadFlow() {
  flowLoading.value = true;
  try {
    const r = await dataConsole.flowOd(0, 500);
    flowRows.value = r.items;
    flowTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    flowLoading.value = false;
  }
}

function openFlowAdd() {
  flowEditId.value = null;
  flowForm.value = { from_yard_code: "", to_yard_code: "", value_teu: 0 };
  flowDlg.value = true;
}

function openFlowEdit(row: any) {
  flowEditId.value = row.id;
  flowForm.value = { ...row };
  flowDlg.value = true;
}

async function saveFlow() {
  try {
    const f = flowForm.value;
    if (flowEditId.value) await dataConsole.flowOdUpdate(flowEditId.value, { value_teu: f.value_teu });
    else await dataConsole.flowOdCreate({ ...f });
    ElMessage.success("已保存");
    flowDlg.value = false;
    loadFlow();
  } catch (e) {
    err(e);
  }
}

async function delFlow(row: any) {
  try {
    await ElMessageBox.confirm("确定删除该 OD？", "确认");
    await dataConsole.flowOdDelete(row.id);
    ElMessage.success("已删除");
    loadFlow();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function importFlowCsv(file: File) {
  try {
    const r = await dataConsole.flowOdImport(file);
    ElMessage.success(`导入：新增 ${r.inserted} 更新 ${r.updated} 失败 ${r.errors?.length || 0}`);
    loadFlow();
  } catch (e) {
    err(e);
  }
  return false;
}

// —— throughput ——
const tpRows = ref<any[]>([]);
const tpTotal = ref(0);
const tpLoading = ref(false);
const tpDlg = ref(false);
const tpEditId = ref<number | null>(null);
const tpForm = ref({ yard_id: 0, stat_date: "", in_teu: 0, out_teu: 0, stock_teu: 0 });

async function loadTp() {
  tpLoading.value = true;
  try {
    const r = await dataConsole.throughput(0, 500);
    tpRows.value = r.items;
    tpTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    tpLoading.value = false;
  }
}

function openTpAdd() {
  tpEditId.value = null;
  tpForm.value = { yard_id: 0, stat_date: "", in_teu: 0, out_teu: 0, stock_teu: 0 };
  tpDlg.value = true;
}

function openTpEdit(row: any) {
  tpEditId.value = row.id;
  tpForm.value = { ...row, stat_date: String(row.stat_date).slice(0, 10) };
  tpDlg.value = true;
}

async function saveTp() {
  try {
    const f = tpForm.value;
    const body = {
      yard_id: f.yard_id,
      stat_date: f.stat_date,
      in_teu: f.in_teu,
      out_teu: f.out_teu,
      stock_teu: f.stock_teu,
    };
    if (tpEditId.value) await dataConsole.throughputUpdate(tpEditId.value, { in_teu: f.in_teu, out_teu: f.out_teu, stock_teu: f.stock_teu });
    else await dataConsole.throughputCreate(body);
    ElMessage.success("已保存");
    tpDlg.value = false;
    loadTp();
  } catch (e) {
    err(e);
  }
}

async function delTp(row: any) {
  try {
    await ElMessageBox.confirm("确定删除？", "确认");
    await dataConsole.throughputDelete(row.id);
    loadTp();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function importTpCsv(file: File) {
  try {
    const r = await dataConsole.throughputImport(file);
    ElMessage.success(`导入：新增 ${r.inserted} 失败 ${r.errors?.length || 0}`);
    loadTp();
  } catch (e) {
    err(e);
  }
  return false;
}

// —— cargo ——
const cargoRows = ref<any[]>([]);
const cargoTotal = ref(0);
const cargoLoading = ref(false);
const cargoDlg = ref(false);
const cargoEditId = ref<number | null>(null);
const cargoForm = ref({ yard_id: 0, category: "", volume: 0 });

async function loadCargo() {
  cargoLoading.value = true;
  try {
    const r = await dataConsole.cargo(0, 500);
    cargoRows.value = r.items;
    cargoTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    cargoLoading.value = false;
  }
}

function openCargoAdd() {
  cargoEditId.value = null;
  cargoForm.value = { yard_id: 0, category: "", volume: 0 };
  cargoDlg.value = true;
}

function openCargoEdit(row: any) {
  cargoEditId.value = row.id;
  cargoForm.value = { ...row };
  cargoDlg.value = true;
}

async function saveCargo() {
  try {
    const f = cargoForm.value;
    if (cargoEditId.value) await dataConsole.cargoUpdate(cargoEditId.value, { category: f.category, volume: f.volume });
    else await dataConsole.cargoCreate({ ...f });
    ElMessage.success("已保存");
    cargoDlg.value = false;
    loadCargo();
  } catch (e) {
    err(e);
  }
}

async function delCargo(row: any) {
  try {
    await ElMessageBox.confirm("确定删除？", "确认");
    await dataConsole.cargoDelete(row.id);
    loadCargo();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function importCargoCsv(file: File) {
  try {
    const r = await dataConsole.cargoImport(file);
    ElMessage.success(`导入：新增 ${r.inserted} 更新 ${r.updated}`);
    loadCargo();
  } catch (e) {
    err(e);
  }
  return false;
}

// —— alerts ——
const alertRows = ref<any[]>([]);
const alertTotal = ref(0);
const alertLoading = ref(false);
const alertDlg = ref(false);
const alertEditId = ref<number | null>(null);
const alertForm = ref({ yard_id: 0, level: "info", alert_type: "", message: "" });

async function loadAlerts() {
  alertLoading.value = true;
  try {
    const r = await dataConsole.alerts(0, 500);
    alertRows.value = r.items;
    alertTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    alertLoading.value = false;
  }
}

function openAlertAdd() {
  alertEditId.value = null;
  alertForm.value = { yard_id: 0, level: "info", alert_type: "", message: "" };
  alertDlg.value = true;
}

function openAlertEdit(row: any) {
  alertEditId.value = row.id;
  alertForm.value = { yard_id: row.yard_id, level: row.level, alert_type: row.alert_type, message: row.message };
  alertDlg.value = true;
}

async function saveAlert() {
  try {
    const f = alertForm.value;
    if (alertEditId.value)
      await dataConsole.alertUpdate(alertEditId.value, { level: f.level, alert_type: f.alert_type, message: f.message });
    else await dataConsole.alertCreate({ ...f });
    ElMessage.success("已保存");
    alertDlg.value = false;
    loadAlerts();
  } catch (e) {
    err(e);
  }
}

async function delAlert(row: any) {
  try {
    await ElMessageBox.confirm("确定删除？", "确认");
    await dataConsole.alertDelete(row.id);
    loadAlerts();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function importAlertCsv(file: File) {
  try {
    const r = await dataConsole.alertImport(file);
    ElMessage.success(`导入：新增 ${r.inserted}`);
    loadAlerts();
  } catch (e) {
    err(e);
  }
  return false;
}

// —— vehicles ——
const vehRows = ref<any[]>([]);
const vehTotal = ref(0);
const vehLoading = ref(false);
const vehDlg = ref(false);
const vehEditId = ref<number | null>(null);
const vehForm = ref({ code: "", from_yard_code: "", to_yard_code: "", progress: 0, status: "running" });

async function loadVeh() {
  vehLoading.value = true;
  try {
    const r = await dataConsole.vehicles(0, 500);
    vehRows.value = r.items;
    vehTotal.value = r.total;
  } catch (e) {
    err(e);
  } finally {
    vehLoading.value = false;
  }
}

function openVehAdd() {
  vehEditId.value = null;
  vehForm.value = { code: "", from_yard_code: "", to_yard_code: "", progress: 0, status: "running" };
  vehDlg.value = true;
}

function openVehEdit(row: any) {
  vehEditId.value = row.id;
  vehForm.value = { ...row };
  vehDlg.value = true;
}

async function saveVeh() {
  try {
    const f = vehForm.value;
    if (vehEditId.value)
      await dataConsole.vehicleUpdate(vehEditId.value, {
        from_yard_code: f.from_yard_code,
        to_yard_code: f.to_yard_code,
        progress: f.progress,
        status: f.status,
      });
    else await dataConsole.vehicleCreate({ ...f });
    ElMessage.success("已保存");
    vehDlg.value = false;
    loadVeh();
  } catch (e) {
    err(e);
  }
}

async function delVeh(row: any) {
  try {
    await ElMessageBox.confirm("确定删除？", "确认");
    await dataConsole.vehicleDelete(row.id);
    loadVeh();
  } catch (e) {
    if (e !== "cancel") err(e);
  }
}

async function importVehCsv(file: File) {
  try {
    const r = await dataConsole.vehicleImport(file);
    ElMessage.success(`导入：新增 ${r.inserted} 更新 ${r.updated}`);
    loadVeh();
  } catch (e) {
    err(e);
  }
  return false;
}
</script>

<style scoped lang="scss">
.data-console {
  min-height: 100vh;
  padding: 20px 24px 40px;
  background: linear-gradient(180deg, #071325 0%, #0a1e38 100%);
  color: #e8f4ff;
  /* 本页内 Element Plus 浅色填充，避免表格条纹、悬停变成白底 */
  --el-fill-color-blank: rgba(12, 38, 68, 0.92);
  --el-fill-color-light: rgba(16, 48, 82, 0.88);
  --el-fill-color-lighter: rgba(22, 58, 98, 0.82);
  --el-fill-color-extra-light: rgba(28, 72, 118, 0.35);
  --el-bg-color: rgba(8, 28, 52, 0.96);
  --el-text-color-primary: #e4f2ff;
  --el-text-color-regular: #c8dff5;
  --el-text-color-secondary: #9ec0e0;
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
}

.help {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(90, 210, 255, 0.28);

  :deep(.el-collapse-item__header) {
    color: #f0fbff;
    font-weight: 600;
    font-size: 14px;
    background: linear-gradient(90deg, rgba(16, 62, 108, 0.95), rgba(10, 40, 72, 0.9));
    padding: 12px 16px;
    min-height: 48px;
    border-bottom: 1px solid rgba(80, 200, 255, 0.22);
  }

  :deep(.el-collapse-item__arrow) {
    color: #7ee9ff;
  }

  :deep(.el-collapse-item__wrap) {
    border-bottom: none;
    background: rgba(5, 22, 42, 0.75);
  }

  :deep(.el-collapse-item__content) {
    padding: 14px 18px 18px;
    color: #e4f2ff;
    background: rgba(5, 22, 42, 0.75);
    font-size: 13px;
    line-height: 1.65;
  }

  ul {
    margin: 0;
    padding-left: 1.25rem;
    list-style: disc;
  }

  li {
    margin-bottom: 6px;
    color: #dceeff;
  }

  li strong {
    color: #7ffff4;
    font-weight: 650;
  }
}

.tabs {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(80, 200, 255, 0.28);
  --el-border-color: rgba(80, 200, 255, 0.32);
  --el-bg-color-overlay: rgba(8, 28, 52, 0.98);

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

  :deep(.el-tabs--border-card > .el-tabs__content) {
    padding: 16px;
    background: rgba(5, 20, 42, 0.82);
    color: #e8f4ff;
  }
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

/* 表格：强制深色底 + 高对比文字（覆盖条纹行默认浅灰底） */
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

:deep(.el-table__border-left-patch),
:deep(.el-table__border-bottom-patch) {
  background-color: rgba(70, 190, 255, 0.22);
}

:deep(.el-table .el-button.is-link.el-button--primary) {
  color: #5ce8ff;
}

:deep(.el-table .el-button.is-link.el-button--danger) {
  color: #ff9aad;
}

.addr-row {
  display: flex;
  gap: 8px;
  width: 100%;
  .el-input {
    flex: 1;
  }
}

</style>
