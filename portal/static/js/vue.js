
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
    template: `<div>
        {{ facet.title }}
        <div v-for="option in facet.modalOptions">
            <input type="checkbox" :value="option" :key="option.value" name="test" v-model="facet.checkedOptions"> {{ option.text }}
        </div>
    </div>`,
    computed: {
        facet() {
            return store.state.facets[this.index];
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
    <div class="modal fade facet-modal" id="facetModal-test" tabindex="-1" role="dialog"  aria-hidden="true">
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
     </div>
                 `,
    computed: {
        facet() {
            return store.state.facets[this.index];
        }
    }
});


/*
Vue.component('facet-modal', {
    props: ['facet_key', 'facet_title', 'list'],

    template: `<div class="modal fade facet-modal" id="facetModal-test" tabindex="-1" role="dialog"  aria-hidden="true">
                 <div class="modal-dialog modal-lg" role="document">
                     <div class="modal-content">
                         <div class="modal-header">
                             <h5 class="modal-title">{{ facet_title }}</h5>
                             <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                 <span aria-hidden="true">&times;</span>
                             </button>
                         </div>
                         <div class="modal-body">
                             <div class="in-facet-search">
                                 <input class="form-control form-control-sm in-facet-search-input">
                             </div>
                             <div class="pt-2 facet-modal-options">
                                 <div v-for="checkedOption in list" class="form-check w-100" data-value="test">
                                     <input class="form-check-input" type="checkbox" :value="checkedOption" :key="checkedOption.value" name="test" v-model="list" checked>
                                     <label class="form-check-label w-100">
                                         <div class="facet-submenu-item">
                                             <div class="d-inline-block text-truncate">{{ checkedOption.text }}</div>
                                             <div><span class="badge badge-pill badge-secondary">test</span></div>
                                         </div>
                                     </label>
                                 </div>
         
                                 <hr>
         
                                 <div v-for="option in options" class="form-check w-100" data-value="test">
                                     <input class="form-check-input" type="checkbox" :value="option" :key="option.value" name="test" v-model="list">
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

    data() {
        return {
            options: [
                {text: 'Czechia', value: 'cz'},
                {text: 'Slovakia', value: 'sk'},
                {text: 'Netherlands', value: 'nl'}
            ],

        }
    },
    model: {
        prop: 'list',
        event: 'listchange'
    },
    computed: {
        listLocal: {
            get: function() {
                return this.list
            },
            set: function(value) {
                this.$emit('listchange', value)
            }
        }
    }
});
*/

const store = new Vuex.Store({
    state: {
        facets: [
            {
                name: 'testfacet',
                title: 'Test Facet',
                field: 'test.facet',
                mostFrequentOptions: [
                    {text: 'Czechia', value: 'cz'},
                ],
                modalOptions: [
                    {text: 'Czechia', value: 'cz'},
                    {text: 'Slovakia', value: 'sk'},
                    {text: 'Netherlands', value: 'nl'}
                ],
                checkedOptions: [],
            },
        ],
    },
    mutations: {
        increment (state) {
            state.count++
        }
    }
});

var vue = new Vue({
    el: '#vue',
    store: store,
    data: {
        list: [],
    },
    /*
    components: {
        facet-modals,
        facet-modal
    },*/
});

