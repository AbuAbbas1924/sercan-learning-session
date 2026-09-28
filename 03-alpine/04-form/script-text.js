console.log('alpine is loaded')
function func1() {
    return {
        'name': 'John',
        'age': 20,
        calling() {
            console.log(`name: ${this.name} and age: ${this.age}`);
        }
    }
};
// const runner = func1();
// runner.calling();
func1().calling();