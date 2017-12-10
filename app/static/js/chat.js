class Messenger {
	constructor() {
		this.messageList = [];
		this.deletedList = [];
		
		this.me = 1; // completely arbitrary id
		this.them = 5; // and another one
		
		this.onRecieve = (message) => console.log('Recieved: ' + message.text);
		this.onSend = (message) => console.log('Sent: ' + message.text);
		this.onDelete = (message) => console.log('Deleted: ' + message.text);
	}
	
	send(text = '') {
		text = this.filter(text);
		
		if (this.validate(text)) {
			let message = {
				user: this.me,
				text: text,
				time: new Date().getTime()
			};
			
			this.messageList.push(message);
			
			this.onSend(message);
		}
	}
	
	recieve(text = '') {
		//text = this.filter(text);
		
		if (this.validate(text)) {
			let message = {
				user: this.them,
				text: text,
				time: new Date().getTime()
			};
			
			this.messageList.push(message);
			
			this.onRecieve(message);
		}
	}
	
	delete(index) {
		index = index || (this.messageLength - 1);
		
		let deleted = this.messageLength.pop();
		
		this.deletedList.push(deleted);
		this.onDelete(deleted);
	}
	
	filter(input) {
		let output = input.replace('bad input', 'good output'); // such amazing filter there right?
		return output;
	}
	
	validate(input) {
		return !!input.length; // an amazing example of validation I swear.
	}
}

class BuildHTML {
	constructor() {
		this.messageWrapper = 'message-wrapper';
		this.circleWrapper = 'circle-wrapper';
		this.textWrapper = 'text-wrapper';
		
		this.meClass = 'me';
		this.themClass = 'them';
	}
	
	_build(text, who) {
		const userIcon = "static/img/user.png";
		const robotIcon = "static/img/robot.png";
		return `<div class="${this.messageWrapper} ${this[who + 'Class']}">
					<div class="${this.circleWrapper} animated bounceIn">
						${who === "me" ? `<img src="${userIcon}" />`
						 : `<img src="${robotIcon}" />`}
					</div>
					<div class="${this.textWrapper}">${text}</div>
				</div>`;
	}
	
	me(text) {
		return this._build(text.replace('\n', '<br />'), 'me');
	}
	
	them(text) {
		return this._build(text.replace('\n', '<br />'), 'them');
	}
}

$(document).ready(function() {
	let messenger = new Messenger();
	let buildHTML = new BuildHTML();

	let $input = $('#input');
	let $send = $('#send');
	let $content = $('#content');
	let $inner = $('#inner');
	
	let player = null;

	function safeText(text) {
		//$content.find('.message-wrapper').last().find('.text-wrapper').text(text);
	}
	
	function animateText() {
		// setTimeout(() => {
			$content.find('.message-wrapper').last().find('.text-wrapper').addClass('animated bounceIn');
		// }, 350)
	}
	
	function scrollBottom() {
		// console.log($($content).height());
		$($inner).animate({
			// scrollTop: $($content).offset().top + $($content).outerHeight(true)
			scrollTop: $($content).height()
		}, {
			queue: false,
			duration: 'ease'
		});
	}
	
	function buildSent(message) {
		// console.log('sending: ', message.text);
		
		$content.append(buildHTML.me(message.text));
		safeText(message.text);
		animateText();
		
		scrollBottom();
	}
	
	function buildRecieved(message) {
		// console.log('recieving: ', message.text);
		
		$content.append(buildHTML.them(message.text));
		safeText(message.text);
		animateText();
		
		scrollBottom();
	}


	function sendMessage() {
		let text = $input.val();
		messenger.send(text);
		$.ajax({
			url: '/',
			data: {'req' : text},
			type: 'POST',
			success: function(response) {
				res = JSON.parse(response);
				setTimeout(() => {
					messenger.recieve(res["text"].replace(/\n/g, '<br>'));
				}, 200)
				if (res["link"] !== '') {
					setTimeout(() => {
						loadVideo(res["link"]);
					}, 1000);
				}
			},
			error: function(error) {
				console.log(error);
			}
		});
		if (text) {
			$input.val('');
			$input.focus();
		}
	}

	function loadVideo(id) {
		if (!player) {
			$('.wrapper').css('flex-basis', '320px');
			$('#ytplayer').css('flex', '1');
			setTimeout(() => {
				player = new YT.Player('ytplayer', {
					height: '100%',
					width: '100%',
					videoId: id
				});
			}, 500);
		} else {
			player.cueVideoById(id);
		}
	}
	
	messenger.onSend = buildSent;
	messenger.onRecieve = buildRecieved;
	
	
	$input.on('keydown', function(e) {
		let key = e.which || e.keyCode;
		
		if (key === 13) { // enter key
			e.preventDefault();
			
			sendMessage();
		}
	});
	var $nav = $('#nav');
	var $wrapper = $('.wrapper');
	var $msgBtn = $('#btnMessage');

	$nav.click(function() {
		if (player) {
			$wrapper.css('height', 0);
			$wrapper.css('flex-basis', 0);
			$msgBtn.css('display', 'block');
			setTimeout(() => {
				$msgBtn.css('opacity', 1);
			}, 100);
		}
	});

	$msgBtn.click(function() {
		$wrapper.css('height', '100%');
		$wrapper.css('flex-basis', '320px');
		$msgBtn.css('opacity', 0);
		setTimeout(() => {
			$msgBtn.css('display', 'none');
		}, 200);
	})

	// Start animation
	setTimeout(() => {
		$('.wrapper').css('flex-basis', '600px');
	}, 800);
});
