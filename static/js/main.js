const id_to_hall_map = {
  '1531' : 'Ratty',
  '1532' : 'VDub',
  '1533' : 'Andrews',
  '1534' : 'Blue Room',
  '1535' : 'Jos',
  '1536' : 'Ivy Room'
}

function onSignIn() {
  gapi.load('auth2', () => {
    console.log('loaded auth2')
  });
  gapi.load('client', () => {
    console.log('loaded client')
  })
  gapi.auth2.getAuthInstance().signIn();
  let googleUser = gapi
  console.log(googleUser)
  console.log("HUHG")
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
}



$(document).ready(() => {
  updateMenu()

  function retrieve_calendar() {

    $.post('/retrieve_calendar', {}, responseJSON => {
      let events = $('#events')

      events.empty()

      for(day in responseJSON) {
        let dayItem = $("<div/>")
          .addClass("day")
          .appendTo(events)
        let dayTitle = $("<div/>")
          .addClass("day-title")
          .text(responseJSON[day]['start'])
          .appendTo(dayItem)
        let eventList = $("<ul/>")
          .addClass("event-list")
          .appendTo(dayItem)
        ls = responseJSON[day]['event_list']
        for(evn in ls){
          let listItem = $('<li/>')
            .addClass('event-list-item')
            .text(ls[evn]['time'] + ' ' + ls[evn]['event'])
            .appendTo(eventList)
        }
      }

      /*let eventList = $("<ul/>")
        .addClass("event-list")
        .appendTo(events.empty())
      for(let i = 0; i < responseJSON.length; i++) {
        let event_item = $('<li/>')
          .addClass('event-item')
          .text(responseJSON[i]['start']+ ' '+responseJSON[i]['event'] )
          .appendTo(eventList)
      }*/
      console.log("ey")

    })
  }
  function retrieve_piazza() {

    $.post('/retrieve_piazza', {}, responseJSON => {

      let events = $('#piazza-notifications')
      let eventList = $("<ul/>")
        .addClass("piazza-event-list")
        .appendTo(events.empty())
      for(let i = 0; i < responseJSON.length; i++) {
        let event_item = $('<li/>')
          .addClass('piazza-event-item')
          .text(responseJSON[i])
          .appendTo(eventList)
      }
      console.log("bay")

    })
  }

  retrieve_calendar()
  retrieve_piazza()



  /**
   * Toggles the top toggle bar on click
   */
  $('.toggle-item').on('click', event => {
    let iden = event['currentTarget'].id

    toggleActive(iden)

  });

  /**
   * Toggles keypresses. Mostly used for shortcuts, '.' puts the todo-text in
   * focus, while 't' adds a task
   * In addition, if you press enter in the todo-text textbox, this will
   * make a new one.
   */
  $(document).keypress(e => {
    if(!$(e.target).is('input')) {
      if(e.key == '.'){
        $('input[name=\'todo-text\']').focus()
      }else if(e.key == 't'){
        addTask()
      }

    } else {
      let box = $('input[name=\'todo-text\']')
      if(box.is(':focus') && e.key == 'Enter'){
        addTask()
      }
    }
  });

  /**
   * If the sectionheading of a meal is double clicked, it is
   * automatically added to the textbox item to put into the calendar.
   */
  $('.meal .section-heading').on('dblclick', event => {
    let eventNameBox = $('input[name=\'event-name\']')
    let item = event['currentTarget'].innerText
    eventNameBox.val(item)
    eventNameBox.focus()
  });



  let numCheckboxes = 1;

  /**
   * Removes a given task, taking in the task as an argument
   */
  function removeTask(target) {
    let parent = target.parent()
    parent.remove()
    numCheckboxes--;

    if(numCheckboxes < 1) {
      addTask()
    }
  }

  /**
   * Upon clicking a checkbox, removes the task from the list
   */
  $(document).on('click', '.checkbox', (event) => {
    removeTask($(event['currentTarget']))

  });

  /**
   * Adds a task to the end of the task list
   */
  function addTask() {
    let todoText = $('<div/>')
      .addClass('todo-text')
      .appendTo($('.todo-list'))

    $('<div/>')
      .addClass('checkbox')
      .appendTo(todoText)

    let todoTextbox = $('<input type=\'text\' name=\'todo-text\' placeholder=\'Task...\'/>')
      .addClass('todo-text')
      .appendTo(todoText)

      numCheckboxes++;

      todoTextbox.focus()
  }

  /**
   * On clicking a food-item, we add that value to the text entry of the calendar
   * and focuses the textbox
   */
  $(document).on('dblclick', '.food-item', event => {
    let eventNameBox = $('input[name=\'event-name\']')
    let item = event['currentTarget'].innerText
    eventNameBox.val(item)
    eventNameBox.focus()
  });

  $(document).on('dblclick', '.piazza-event-item', event => {
    let eventNameBox = $('input[name=\'event-name\']')
    let item = event['currentTarget'].innerText
    eventNameBox.val(item)
    eventNameBox.focus()
  });

  /**
   * Given the id of a dining hall, toggles the activeness of that particular
   * dining hall, meaning showing/hiding it in the main panels and fading/bolding
   * it in the status bar.
   */
  function toggleActive(id) {
    let active = $(`.toggle-item[id=\'${id}\']`)
    let item = $(`.meal[id=\'${id}\']`)

    if(active.hasClass('active')) {
      active.removeClass('active')
      item.hide()
    } else {
      active.addClass('active')
      item.show()
    }
  }
  /**
   * Sets a given dining id to be active
   */
  function setActive(id) {
    let active = $(`.toggle-item[id=\'${id}\']`)
    let item = $(`.meal[id=\'${id}\']`)

    if(!active.hasClass('active')) {
      active.addClass('active')
      item.show()
    }

  }
  /**
   * Sets a given dining id to be inactive
   */
  function setNotActive(id) {
    let active = $(`.toggle-item[id=\'${id}\']`)
    let item = $(`.meal[id=\'${id}\']`)

    if(active.hasClass('active')) {
      active.removeClass('active')
      item.hide()
    }
  }

  /**
   * Sets an interval every 6 hours to audomatically update the menu
   */
  setInterval(() => {
    updateMenu()

  },  6 * 60 * 60 * 1000) // every 6 hours we refresh the menu

  setInterval(() => {
    retrieve_calendar()
    retrieve_piazza()

  }, 60 * 1000)

  /**
   * Queries the server to update the menu.
   */
  function updateMenu() {
    $.post("/get_menu", {}, responseJSON => {

      for(let item in responseJSON) {

        let meal = $(`.meal[id=\'${item}\']`)
        let menu = $(`.meal[id=\'${item}\'] .menu`)

        let day_part_list = $("<ul/>")
          .addClass("menuList")
          .appendTo(menu.empty())


        if(jQuery.isEmptyObject(responseJSON[item])) {
          menu.text("No food today soz :(")
          setNotActive(item)
        } else {

          day_parts = responseJSON[item]
          for(let i = 0; i < day_parts.length; i++) {

            part = day_parts[i]['label']

            let day_part_list_item = $('<li/>')
              .addClass("menu-list-item")
              .text(part)
              .appendTo(day_part_list)

            let station_list = $('<ul/>')
              .addClass("station-list")
              .appendTo(day_part_list_item)

            let stations = day_parts[i]['stations']
            for(let station in stations) {
              let station_list_item = $('<li/>')
                .addClass("station-list-item")
                .text(station)
                .appendTo(station_list)

              let food_list = $('<ul/>')
                .addClass("food-list")
                .appendTo(station_list_item)

              let foods = stations[station]
              for(let j = 0; j < foods.length; j++) {
                let food_list_item = $('<li/>')
                  .addClass("food-item")
                  .text(foods[j])
                  .appendTo(food_list)
              }
            }
          }
          setActive(item)

        }
      }


    });
  }

  /**
   * Adds a given event to the calendar, given the inputs of event-name and when
   * textboxes
   */
  function updateCalendar() {
    let eventNameBox = $('input[name=\'event-name\']')
    let whenBox = $('input[name=\'when\']')
    let eventName = eventNameBox.val()
    let when = whenBox.val()
    if(eventName == '' || when == '') {
      return;
    }
    $.post("/add_to_calendar",
      {'eventName' : eventName, 'when' : when},
      response => {
        showMessage(response)
    })

  }

  /**
   * Displays a given message for 5 seconds in the message bar
   */
  function showMessage(msg) {
    let messageDiv = $('#message')
    messageDiv.text(msg)
    messageDiv.fadeIn('slow').delay(5000).fadeOut('slow')

  }

  /**
   * Updates the menu upon clicking the update menu button
   */
  $('#updateMenu').on('click', event => {
    showMessage("Loading...")
    updateMenu()

  });
  /**
   * Sends a request to the calendar upon clicking the button
   */
  $('#updateCalendar').on('click', event => {
    updateCalendar()
  });


});
