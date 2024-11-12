// src/main.js
import Vue from "vue";
import Vuetify from "vuetify";
import DaySpanVuetify from "dayspan-vuetify";
import App from "./App.vue";
import router from './router';

// 导入 Element-UI 样式
import "element-ui/lib/theme-chalk/index.css";

// 导入 Vuetify 样式
import "vuetify/dist/vuetify.min.css";

// 导入 Material Design Icons
import "material-design-icons-iconfont/dist/material-design-icons.css";

// 导入 DaySpanVuetify 样式
import "dayspan-vuetify/dist/lib/dayspan-vuetify.min.css";

// 导入 Element-UI 组件
import {
  Button,
  Form,
  FormItem,
  Input,
  Message,
  Container,
  Header,
  Aside,
  Main,
  Menu,
  Submenu,
  MenuItem,
  MenuItemGroup,
  Tag,
  Table, // 添加 Table 组件
  TableColumn // 添加 TableColumn 组件
} from "element-ui";

Vue.config.productionTip = false;

// 注册 Element-UI 组件
Vue.use(Tag);
Vue.use(Button);
Vue.use(Form);
Vue.use(FormItem);
Vue.use(Input);
Vue.use(Container);
Vue.use(Header);
Vue.use(Aside);
Vue.use(Main);
Vue.use(Menu);
Vue.use(Submenu);
Vue.use(MenuItem);
Vue.use(MenuItemGroup);
Vue.use(Table); // 注册 Table 组件
Vue.use(TableColumn); // 注册 TableColumn 组件
Vue.prototype.$message = Message;

// 注册 Vuetify 并配置主题
Vue.use(Vuetify, {
  theme: {
    primary: "#1976d2",
    secondary: "#424242",
    accent: "#82B1FF",
    error: "#FF5252",
    info: "#2196F3",
    success: "#4CAF50",
    warning: "#FFC107",
  },
});

// 注册 DaySpanVuetify
Vue.use(DaySpanVuetify, {
  methods: {
    getDefaultEventColor: () => "#1976d2",
  },
});

new Vue({
  el: "#app",
  router,
  render: (h) => h(App),
});