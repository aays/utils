# evol2018 metal shirts

library(dplyr)
library(ggplot2)
library(magrittr)

s <- data.frame(day = c(18:22), 
                shirts = c(4, 6, 8, 12, 14),
                daily = c(4, 2, 2, 4, 2))

s %<>% mutate(day = paste('Aug', day))
s

s_plot <- ggplot(s, aes(x = day, y = shirts)) +
  geom_point(size = 3) +
  geom_line(aes(group = 1), size = 1.2) +
  theme(plot.title = element_text(family = "Helvetica", hjust = 0.5, size = 18),
        axis.title.y = element_text(family = "Helvetica", size = 18),
        axis.text.x = element_text(family = "Helvetica", size = 20, color = 'black',
                                   hjust = 1, angle = 45),
        axis.text.y = element_text(family = "Helvetica", size = 18, color = 'black'),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.line = element_line(colour = 'black', linetype = 'solid', size = 1.2),
        plot.tag = element_text(family = "Helvetica", size = 18, color = 'black', face = 'bold'),
        panel.background = element_blank(),
        axis.ticks = element_blank()) +
  scale_y_continuous(breaks = seq(0, 16, 4)) +
  coord_cartesian(y = c(0, 16)) +
  xlab('') +
  ggtitle('cumulative count of metal band shirts at #evol2018')

s_plot

ggsave('evol2018shirts.png', plot = s_plot, path = 'Desktop',
       height = par('din')[1], width = par('din')[1])
