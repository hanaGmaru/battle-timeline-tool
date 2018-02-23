<template>
  <div>
    <div v-for="skill in skill_data.common">
      <img v-bind:src="'/static/img/skill_icon/' + skill.icon" />
      <div v-for="action in skill.actions">
        <img v-bind:src="'/static/img/skill_icon/' + action.icon" />
        <div> {{action}} </div>
      </div>
    </div>

    <div v-for="skill in skill_data.only">
      <img v-bind:src="'/static/img/skill_icon/' + skill.icon" />
      <div v-for="action in skill.actions">
        <img v-bind:src="'/static/img/skill_icon/' + action.icon" />
        <div> {{action}} </div>
      </div>
    </div>
  </div>
</template>

<script>
import skillData from '@/assets/skill_data'

export default {
  // name: 'HelloWorld',
  data () {
    return {
      // msg: 'Welcome to Your Vue.js App'
    }
  },
  computed: {
    skill_data () {
      return skillData
    }
  }
}
</script>

<style scoped>
</style>
