# web pages

class webpages(object):
    def __init__(self):
        print("Web page initialisation")
        pass
    
    def steerpage(self):
            #Template HTML
        html =  """
            <!DOCTYPE html>
            <html>
                <head>
                <title>Wheel Chair</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; text-align: center; margin:0px auto; padding-top: 30px;}
                table { margin-left: auto; margin-right: auto; }
                td { padding: 8 px;  }
                .button {
                background-color: Tomato; border: none; border-radius: 10px; color: white; padding: 10px 20px;
                text-align: center; text-decoration: none; display: inline-block; font-size: 18px; margin: 6px 3px;
                cursor: pointer; -webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none;
                -moz-user-select: none; -ms-user-select: none; user-select: none; -webkit-tap-highlight-color: rgba(0,0,0,0);
                }
            </style>
            </head>
            <body>
                <h1>Wheel Chair</h1>
                <br>
                <p id="demo"></p>
                <table>
                <tr><td colspan="3" align="center"><button class="button" 
                onmousedown="sndCmd('FWD');" ontouchstart="sndCmd('FWD');" 
                >Forward</button></td></tr>
                <tr><td align="center"><button class="button" 
                onmousedown="sndCmd('LEFT');" ontouchstart="sndCmd('LEFT');" 
                >Left</button></td>
                <td align="center"><button class="button" 
                onmousedown="sndCmd('STOP');" ontouchstart="sndCmd('STOP');"
                >Stop</button></td>
                <td align="center"><button class="button" 
                onmousedown="sndCmd('RIGHT');" ontouchstart="sndCmd('RIGHT');" 
                >Right</button></td>
                </tr>                  
                <tr><td colspan="3" align="center"><button class="button" 
                onmousedown="sndCmd('REV');" ontouchstart="sndCmd('REV');" 
                >Reverse</button></td></tr>
                <tr><td colspan="2" align="center"><button class="button" 
                onmousedown="sndCmd('FOLLOW');" ontouchstart="sndCmd('FOLLOW');" 
                >Line Following</button></td>
                <td align="center"><button class="button" 
                onmousedown="sndCmd('STEERING');" ontouchstart="sndCmd('STEERING');"
                >Steering</button></td>            
                </tr> 
                <tr><td colspan="3" align="center"><button class="button" 
                onmousedown="sndCmd('EXIT');" ontouchstart="sndCmd('EXIT');" onmouseup="sndCmd('EXIT');" ontouchend="sndCmd('EXIT');"
                >Exit</button></td></tr>
            </table>
            <script>
                function sndCmd(x) {
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", "/action?go=" + x, true);
                    xhr.send();
                }
            </script>
            </body>
            </html>
            """
        return str(html)
