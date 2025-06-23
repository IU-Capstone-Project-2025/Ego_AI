import { MapPinIcon } from "lucide-react";
import { Avatar, AvatarImage } from "../../components/ui/avatar";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Card, CardContent } from "../../components/ui/card";
import Footer from "../../components/ui/footer";

export const General = (): JSX.Element => {
  const navItems = [
    "НАШИ ПРОДУКТЫ",
    "О ПРОЕКТЕ",
    "КАК НАСТРОИТЬ",
    "ОТЗЫВЫ",
    "ЦЕНТР ПОДДЕРЖКИ",
  ];

  const featureCards = [
        {
          title: "Meet your AI executive assistant",
          image: "https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154430/card1-1_texruy.svg",
          width: "w-[584px]",
          imageClass: "w-[561px] h-[310px] top-[11px] left-3 absolute object-cover",
        },
        {
          title: "Brainstorm with a prompt",
          image: "https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154427/card1-2_lokxhq.svg",
          width: "w-[584px]",
          imageClass: "w-[561px] top-[11px] absolute h-[310px] left-[11px]",
        },
        {
          title: "Smart Focus Feature",
          image: "https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154426/card2-1_lxunde.svg",
          width: "w-[366px]",
          imageClass: "w-[345px] top-2.5 absolute h-[310px] left-[11px]",
        },
        {
          title: "Find a place to visit with geo-assistance",
          image: "https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154425/card2-2_uxjsy9.svg",
          width: "w-[389px]",
          imageClass:
            "w-[367px] h-[310px] top-2.5 left-[11px] absolute object-cover",
        },
        {
          title: "Uncover new activities with\nrecomendations",
          image: "https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154422/card2-3_l2lwtu.svg",
          width: "w-[389px]",
          imageClass:
            "w-[364px] h-[295px] top-[25px] left-[13px] absolute object-cover",
        },
      ];

  return (
    <div className="bg-white w-full">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 relative">
        {/* Header */}
        <header className="w-full py-6 flex flex-wrap justify-between items-center gap-4">
          <div className="text-3xl font-extrabold">
            <span className="text-[#ce5aed]">EGO</span>
            <span className="text-[#ce5aed]">:</span>
            <span className="text-[#66d6b8]">AI</span>
          </div>

          <nav className="hidden lg:flex gap-6">
            {navItems.map((item, i) => (
              <Button
                key={i}
                variant="link"
                className="text-xs text-[#757575] font-semibold"
              >
                {item}
              </Button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <MapPinIcon className="w-5 h-5 text-[#757575]" />
            <div className="text-xs font-semibold text-[#757575]">
              INNOPOLIS,
              <br />
              1, UNIVERSITETSKAYA ST.
            </div>
          </div>
        </header>

        {/* Hero Section */}

        <div className="relative w-full max-w-[1440px] mx-auto pt-20 px-4 sm:px-6 lg:px-8 pb-48 min-h-[1100px]">
        {/* Фоновые элементы */}
        <div
          className="absolute bg-[#a2ebd4] rounded-[306px/181.81px] blur-[150px] -rotate-[19deg]"
          style={{
            width: "612px",
            height: "364px",
            top: "712px",
            left: "168px",
            filter: "blur(150px)",
            transformOrigin: "center",
          }}
        >
        </div>

        <div className="absolute text-[300px] font-[Montserrat_Subrayada] font-normal text-[#ffffffdb] tracking-[-6px] leading-[330px]" style={{top: "739px", left: "382px"}}>
          &amp;
        </div>

        <div className="absolute top-[837px] left-[492px] font-[Manrope] font-bold text-[#232323] text-[40px] tracking-[-1.2px] leading-[76px] max-w-xs sm:max-w-md">
          MAKE BETTER MOVES.
          <br />
          STAY ON TOP OF TASKS.
        </div>

        <img
          src="https://res.cloudinary.com/dotrf8vg1/image/upload/v1750154873/Ellipse_20_aevaii.svg"
          alt="Ellipse"
          className="absolute top-[424px] left-[203px] w-[1237px] max-w-full h-auto object-contain"
        />

        <img
          src="https://c.animaapp.com/mc06z6iljxEugW/img/pic.png"
          alt="Pic"
          className="absolute top-0 left-10 w-[1360px] max-w-full h-auto"
        />

    <Card className="absolute w-[620px] h-[700px] top-10 left-[740px] bg-white rounded-[25px] border-none shadow-none">
        <CardContent className="flex flex-col w-[540px] h-[397px] items-center gap-10 absolute top-20 left-10 p-0">
          <div className="relative self-stretch w-full h-40">
            <div className="flex justify-center">
              <Badge className="[font-family:'Manrope',Helvetica] font-semibold text-[#757575] text-xs text-center tracking-[0.24px] leading-3 bg-transparent hover:bg-transparent">
                ПЕРВЫЙ ИИ-ПОМОЩНИК ДЛЯ ДОСТИЖЕНИЯ ЦЕЛЕЙ
              </Badge>
            </div>

            <div className="absolute w-[540px] top-[31px] left-0 [font-family:'Manrope',Helvetica] font-bold text-[50px] text-center tracking-[-1.00px] leading-[55.0px]">
              <span className="text-[#232323] tracking-[-0.50px]">
                Твой{" "}
              </span>
              <span className="text-[#ce5aed] tracking-[-0.50px]">
                VIRTUAL
              </span>
              <span className="text-[#5aa289] tracking-[-0.50px]">
                &nbsp;
              </span>
              <span className="text-[#232323] tracking-[-0.50px]">
                ассистент
              </span>
            </div>
          </div>

          <div className="relative self-stretch [font-family:'Manrope',Helvetica] font-normal text-[#232323] text-xl text-center tracking-[0] leading-[26px]">
            <span className="font-bold">
              Инновации будущего - позволь им работать на тебя.
              <br />
            </span>
            <span className="text-lg leading-[23.4px]">
              Личный ИИ-агент помогает в управлении задачами, занимается
              автоматическим планированием и адаптируется под твои нужды.
            </span>
          </div>

          <Button
            className="w-[300px] h-[50px] bg-[#66d6b8] rounded-[10px] hover:bg-[#5ac1a6] transition-colors"
            onClick={() => window.location.href = "/reg-page"}
          >
            <span className="[font-family:'Manrope',Helvetica] font-bold text-[#232323] text-xs text-center tracking-[0.24px] leading-3 whitespace-nowrap">
              НАЧАТЬ ИСПОЛЬЗОВАТЬ
            </span>
          </Button>
        </CardContent>

        <div className="flex w-80 items-center gap-3 absolute top-[610px] left-[150px]">
          <div className="inline-flex items-center relative flex-[0_0_auto]">
            {[1, 2, 3, 4].map((index) => (
              <Avatar
                key={index}
                className={`relative w-[50px] h-[50px] ${index > 1 ? "-ml-2.5" : ""}`}
              >
                <AvatarImage
                  src={`/assets/imgs/ava${index}.svg`}
                  alt={`User ${index}`}
                  className="object-cover"
                />
              </Avatar>
            ))}
          </div>

          <div className="inline-flex flex-col items-start gap-2.5 relative flex-[0_0_auto]">
            <img
              className="relative flex-[0_0_auto]"
              alt="Stars"
              src="https://res.cloudinary.com/dotrf8vg1/image/upload/v1750163043/stars_lh8bgb.svg"
            />

            <div className="relative w-fit [font-family:'Manrope',Helvetica] font-normal text-[#232323] text-[13px] text-center tracking-[0] leading-[16.9px] whitespace-nowrap">
              <span className="font-bold">10 тыс+</span>
              <span className="[font-family:'Manrope',Helvetica] font-normal text-[#232323] text-[13px] tracking-[0] leading-[16.9px]">
                {" "}
                отзывов!
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Special offer card */}
      <Card className="inline-flex items-center gap-[15px] p-5 absolute top-[640px] left-[375px] bg-[#ffffff1a] rounded-[25px] border-[1.5px] border-solid border-white backdrop-blur-[17px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(17px)_brightness(100%)]">
        <CardContent className="flex items-center gap-[15px] p-0">
          <div className="relative w-[60px] h-[60px] bg-[#ce5aed] rounded-[15px] flex items-center justify-center">
            <img
              className="w-5 h-5"
              alt="Subtract"
              src="https://c.animaapp.com/mc06z6iljxEugW/img/subtract.svg"
            />
          </div>

          <div className="flex flex-col w-[230px] items-start gap-[7px] relative">
            <Badge className="relative self-stretch mt-[-1.00px] [font-family:'Manrope',Helvetica] font-semibold text-[#454545] text-xs tracking-[0.24px] leading-3 bg-transparent hover:bg-transparent">
              СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ
            </Badge>

            <div className="relative self-stretch [font-family:'Manrope',Helvetica] font-normal text-[#454545] text-[13px] tracking-[0] leading-[16.9px]">
              первый месяц - скидка 20% на использование сервиса
            </div>
          </div>
        </CardContent>
      </Card>

        </div>


      <section className="py-16 max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-xl font-light text-[#232323] mb-8 text-center">
            Every feature is designed to minimize effort needed to organize your time.
        </h2>
        <div className="flex flex-wrap gap-5 justify-center">
          {featureCards.slice(0, 2).map((card, i) => (
            <Card
              key={i}
              className={`${card.width} h-[427px] bg-[#d9d8dd] rounded-[40px] border-none relative`}
            >
              <CardContent className="p-0">
                <img
                  className={card.imageClass}
                  alt={card.title}
                  src={card.image}
                />
                <div
                  className="absolute w-[561px] top-[334px] left-5 font-semibold text-[#232323] text-[26px] tracking-[-0.52px] leading-[31.2px]"
                  style={{ fontFamily: "'Manrope', Helvetica" }}
                >
                  {card.title}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="flex flex-wrap gap-5 justify-center mt-10">
          {featureCards.slice(2, 5).map((card, i) => (
            <Card
              key={i + 2}
              className={`${card.width} h-[427px] bg-[#d9d8dd] rounded-[40px] border-none relative`}
            >
              <CardContent className="p-0">
                <img
                  className={card.imageClass}
                  alt={card.title}
                  src={card.image}
                />
                <div
                  className="absolute top-[325px] left-5 font-semibold text-[#232323] text-[26px] tracking-[-0.52px] leading-[31.2px]"
                  style={{ fontFamily: "'Manrope', Helvetica", whiteSpace: 'normal' }}
                >
                  {card.title}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

        <Footer
          ctaButton={{ label: "Partnership program", href: "#" }}
          logo={<span className="text-purple-600 text-[28px]">🅰</span>}
        />
      </div>
    </div>
  );
};

