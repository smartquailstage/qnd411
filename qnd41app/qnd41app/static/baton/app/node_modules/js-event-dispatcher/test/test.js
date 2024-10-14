/* global describe, it, beforeEach */
import EventDispatcher from '../src/EventDispatcher'
import assert from 'assert'

describe('EventDispatcher', function () {
  describe('evtName()', function () {
    it('should prepend the on_ prefix', function () {
      assert.equal(EventDispatcher.evtName('event'), 'on_event')
    })
  })

  describe('register()', function () {
    it('should add a callback binded with this by default', function () {
      assert.equal(EventDispatcher._listeners['on_event'], undefined)
      let myfunc = () => {}
      EventDispatcher.register('event', myfunc)
      assert.equal(EventDispatcher._listeners['on_event'][0][0], EventDispatcher)
      assert.equal(EventDispatcher._listeners['on_event'][0][1], myfunc)
    })

    it('should add a callback binded to the given param', function () {
      assert.equal(EventDispatcher._listeners['on_event2'], undefined)
      let myfunc = () => {}
      let obj = {}
      EventDispatcher.register('event2', myfunc, obj)
      assert.equal(EventDispatcher._listeners['on_event2'][0][0], obj)
      assert.equal(EventDispatcher._listeners['on_event2'][0][1], myfunc)
    })
  })

  describe('unregister()', function () {
    let myfunc2 = () => {}

    it('should remove all event registered function if no callback is given', function () {
      EventDispatcher.register('event', myfunc2)
      assert.equal(EventDispatcher._listeners['on_event'].length, 2)
      EventDispatcher.unregister('event')
      assert.equal(EventDispatcher._listeners['on_event'], undefined)
    })

    it('should remove only one callback if given', function () {
      let myfunc = () => {}
      EventDispatcher.register('event', myfunc)
      EventDispatcher.register('event', myfunc2)
      assert.equal(EventDispatcher._listeners['on_event'].length, 2)
      EventDispatcher.unregister('event', myfunc)
      assert.equal(EventDispatcher._listeners['on_event'].length, 1)
      assert.equal(EventDispatcher._listeners['on_event'][0][1], myfunc2)
    })

    it('should remove nothing if callback doesn\'t match', function () {
      let myfunc = () => {}
      let mywrongfunc = () => {}
      EventDispatcher.register('event3', myfunc)
      assert.equal(EventDispatcher._listeners['on_event3'].length, 1)
      EventDispatcher.unregister('event3', mywrongfunc)
      assert.equal(EventDispatcher._listeners['on_event3'].length, 1)
    })
  })

  describe('emit()', function () {
    let value, value2, eventName, eventName2
    let param, param2, param3, myfunc, myfunc2

    beforeEach(() => {
      EventDispatcher.unregister('emit')
      value = 1
      value2 = 1
      eventName = null
      eventName2 = null
      param = null
      param2 = null
      param3 = null
      myfunc = (e, p) => { value = 2; eventName = e; param = p }
      myfunc2 = (e, p, pp) => { value2 = 2; eventName2 = e; param2 = p; param3 = pp }
      EventDispatcher.register('emit', myfunc)
      EventDispatcher.register('emit', myfunc2)
    })

    it('should call all the regitered callbacks, passing the event name as first argument', function () {
      assert.equal(value, 1)
      assert.equal(value2, 1)
      assert.equal(eventName, null)
      assert.equal(eventName2, null)
      EventDispatcher.emit('emit')
      assert.equal(value, 2)
      assert.equal(value2, 2)
      assert.equal(eventName, 'emit')
      assert.equal(eventName2, 'emit')
    })

    it('should pass the right params to the regitered callbacks', function () {
      assert.equal(param, null)
      assert.equal(param2, null)
      EventDispatcher.emit('emit', 'lol', 'foo')
      assert.equal(param, 'lol')
      assert.equal(param2, 'lol')
      assert.equal(param3, 'foo')
    })

    it('should not call regitered callbacks if event is different ', function () {
      assert.equal(value, 1)
      assert.equal(value2, 1)
      EventDispatcher.emit('emit2')
      assert.equal(value, 1)
      assert.equal(value2, 1)
    })
  })
})
