self.onmessage = function(event) {
    if (event.data === 'startMining') {
      console.log("Mining started in worker");
      // محاكاة عملية التعدين
      let progress = 0;
      let interval = setInterval(function() {
        progress += 10;
        self.postMessage(progress);
        console.log("Mining progress:", progress);
  
        if (progress >= 100) {
          clearInterval(interval);
          self.postMessage("MiningComplete");
          console.log("Mining completed");
        }
      }, 1000);
    }
  };
  