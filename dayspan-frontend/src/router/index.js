import Vue from 'vue';
import Router from 'vue-router';
import CalendarView from '../components/CalendarView.vue';
import SearchView from '../components/SearchView.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Calendar',
      component: CalendarView
    },
    {
      path: '/search',
      name: 'Search',
      component: SearchView
    }
  ]
});
