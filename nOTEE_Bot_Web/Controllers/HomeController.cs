using nOTEE_Bot_Web.Models;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace nOTEE_Bot_Web.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }

        public ActionResult About()
        {
            ViewBag.Message = "Your application description page.";

            return View();
        }

        public ActionResult Chat(Input_Query IQ)
        {
            ProcessStartInfo psi = new ProcessStartInfo(@"python.exe");
            psi.Arguments = "\"" + Path.Combine(Server.MapPath("~/Python"), "Script.py") + "\" -q \"" + IQ.InputText.Trim() + "\"";
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;
            psi.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            psi.UseShellExecute = false;
            Process proc = Process.Start(psi);
            StreamReader myOutput = proc.StandardOutput;
            StreamReader myError = proc.StandardError;
            proc.WaitForExit();

            string Reply = "Sorry! I couldn't find anything";
            string ST = "";
            string QA = "";

            if (proc.HasExited)
            {
                string data = myOutput.ReadToEnd();
                string error = myError.ReadToEnd();

                if (data.Contains("[ST]"))
                {
                    ST = data.Split(new[] { "[ST]" }, StringSplitOptions.None)[1].Trim();
                }

                if (data.Contains("[QA]"))
                {
                    QA = data.Split(new[] { "[QA]" }, StringSplitOptions.None)[1].Split(new[] { "[ST]" }, StringSplitOptions.None)[0].Trim();
                }

                if (QA.Length > 0 && ST.Length > 0)
                {
                    Reply = "<b>" + QA + "</b>" + Environment.NewLine +
                    "<br />" + ST;
                }
            }

            return new JsonResult { Data = new { Reply = Reply } };
        }

        public ActionResult Contact()
        {
            ViewBag.Message = "Your contact page.";

            return View();
        }
    }
}