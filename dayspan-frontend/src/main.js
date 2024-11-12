// src/main.js
import Vue from "vue";
import Vuetify from "vuetify";
import DaySpanVuetify from "dayspan-vuetify";
import App from "./App.vue";
import router from './router';

// ���� Element-UI ��ʽ
import "element-ui/lib/theme-chalk/index.css";

// ���� Vuetify ��ʽ
import "vuetify/dist/vuetify.min.css";

// ���� Material Design Icons
import "material-design-icons-iconfont/dist/material-design-icons.css";

// ���� DaySpanVuetify ��ʽ
import "dayspan-vuetify/dist/lib/dayspan-vuetify.min.css";

// ���� Element-UI ���
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
  Table, // ��� Table ���
  TableColumn // ��� TableColumn ���
} from "element-ui";

Vue.config.productionTip = false;

// ע�� Element-UI ���
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
Vue.use(Table); // ע�� Table ���
Vue.use(TableColumn); // ע�� TableColumn ���
Vue.prototype.$message = Message;

// ע�� Vuetify ����������
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

// ע�� DaySpanVuetify
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