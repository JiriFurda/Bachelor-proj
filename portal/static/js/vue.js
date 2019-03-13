
Vue.component('sidebar-facet-list', {
    template: `<div><sidebar-facet v-for="(facet, index) in facets" :index="index"></sidebar-facet></div>`, // <div v-for="facet in store.facets">TEST</div><
    computed: {
        facets() {
            return store.state.facets;
        }
    }
});

Vue.component('sidebar-facet', {
    props: ['index'],
    template: `
    <div>
        {{ facet.title }}
        <div v-for="option in visibleOptions">
            <input type="checkbox" :value="option" :key="option.value" name="test" v-model="facet.checkedOptions"> {{ option.text }}
        </div>
        <button type="button"
                class="btn btn-sm btn-link more-facets"
                title="test"
                data-toggle="modal"
                :data-target="'#facetModal-' + facet.name"
        >
            More...
        </button>
    </div>`,
    computed: {
        facet() {
            return store.state.facets[this.index];
        },
        visibleOptions() {
            let additionalOptionsCount = Math.max(0, 5 - this.facet.checkedOptions.length); // How many options are missing to be more than five shown overall
            let additionalOptions = this.facet.mostFrequentOptions; // Retrieve additional options
            let checkedOptions = this.facet.checkedOptions;
            additionalOptions = additionalOptions.filter(function(item, pos) {
                return checkedOptions.indexOf(item) === -1;
            }); // Filter out those already selected
            additionalOptions = additionalOptions.slice(0, additionalOptionsCount); // Pick only the amount needed to show at least five
            let resultOptions = this.facet.checkedOptions.concat(additionalOptions); // Merge selected and filling options
            return resultOptions;
        }
    }
});

Vue.component('modal-facet-list', {
    template: `<div><modal-facet v-for="(facet, index) in facets" :index="index"></modal-facet></div>`, // <div v-for="facet in store.facets">TEST</div><
    computed: {
        facets() {
            return store.state.facets;
        }
    }
});

Vue.component('modal-facet', {
    props: ['index'],
    template: `
    <div class="modal fade facet-modal" :id="'facetModal-' + facet.name" tabindex="-1" role="dialog"  aria-hidden="true">
         <div class="modal-dialog modal-lg" role="document">
             <div class="modal-content">
                 <div class="modal-header">
                     <h5 class="modal-title">{{ facet.title }}</h5>
                     <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                         <span aria-hidden="true">&times;</span>
                     </button>
                 </div>
                 <div class="modal-body">
                     <div class="in-facet-search">
                         <input class="form-control form-control-sm in-facet-search-input">
                     </div>
                     <div class="pt-2 facet-modal-options">
                         <div v-for="option in facet.checkedOptions" class="form-check w-100">
                             <input type="checkbox" class="form-check-input" :value="option" :key="option.value" name="test" v-model="facet.checkedOptions">
                             <label class="form-check-label w-100">
                                 <div class="facet-submenu-item">
                                     <div class="d-inline-block text-truncate">{{ option.text }}</div>
                                     <div><span class="badge badge-pill badge-secondary">test</span></div>
                                 </div>
                             </label>
                         </div>
    
                         <hr>
    
                         <div v-for="option in facet.modalOptions" class="form-check w-100">
                             <input type="checkbox" class="form-check-input" :value="option" :key="option.value" name="test" v-model="facet.checkedOptions">
                             <label class="form-check-label w-100">
                                 <div class="facet-submenu-item">
                                     <div class="d-inline-block text-truncate">{{ option.text }}</div>
                                     <div><span class="badge badge-pill badge-secondary">test</span></div>
                                 </div>
                             </label>
                         </div>
                     </div>
                 </div>
                 <div class="modal-footer">
                     <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                     <button type="button" class="btn btn-primary">Save changes</button>
                 </div>
             </div>
         </div>
     </div>`,
    computed: {
        facet() {
            return store.state.facets[this.index];
        }
    }
});

const store = new Vuex.Store({
    state: {
        facets: [
            /*{
                name: 'testfacet',
                title: 'Test Facet',
                field: 'test.facet',
                mostFrequentOptions: [
                    {text: 'Czechia', value: 'cz'},
                    {text: 'Czechia2', value: 'cz2'},
                    {text: 'Czechia3', value: 'cz3'},
                    {text: 'Czechia4', value: 'cz4'},
                    {text: 'Czechia5', value: 'cz5'},
                ],
                modalOptions: [
                    {text: 'Czechia', value: 'cz'},
                    {text: 'Czechia2', value: 'cz2'},
                    {text: 'Czechia3', value: 'cz3'},
                    {text: 'Czechia4', value: 'cz4'},
                    {text: 'Czechia5', value: 'cz5'},
                    {text: 'Slovakia', value: 'sk'},
                    {text: 'Netherlands', value: 'nl'},
                ],
                checkedOptions: [],
            },*/
        ],
    },
    mutations: {
        initFacetData (state, payload) {
            state.facets = payload;
        }
    }
});

Vue.component('init-facet-data', {
    props: ['input'],
    template: '<div></div>',
    mounted() {
        store.commit('initFacetData', this.input);
    }
});

var vue = new Vue({
    el: '#vue',
    store: store,
    data: {
        list: [],
    },
});

